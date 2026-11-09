#!/usr/bin/env python3
"""Compile extracted upstream control functions against deterministic host stubs.

This is NOT an ESP32/AVR target build, radio test, timing measurement, or flight
test. The source paths must point at the pinned source described in firmware/.
Only the locally compiled, generated test program is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


def function(source, name):
    match = re.search(r"\b" + name + r"\s*\([^;{}]*\)\s*\{", source)
    if not match:
        raise ValueError(f"Function not found: {name}")
    start = source.rfind("\n", 0, match.start()) + 1
    opening = source.index("{", match.start())
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


def compile_run(code, name):
    with tempfile.TemporaryDirectory(prefix="xs-drone-host-") as work:
        src = Path(work) / f"{name}.cpp"
        exe = Path(work) / name
        src.write_text(code)
        subprocess.run(["g++", "-std=c++17", "-O1", "-Wall", "-Wextra",
                        "-Wno-unused-parameter", str(src), "-o", str(exe)], check=True)
        return subprocess.check_output([str(exe)], text=True).strip()


PREAMBLE = r'''
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <cmath>
using std::isfinite;
static int checks=0;
void check(bool value) { ++checks; if (!value) { fprintf(stderr,"Check %d failed\n",checks); exit(1); } }
'''


def esp_test(root):
    base = root / "Firmware/esp-drone"
    modules = base / "components/core/crazyflie/modules"
    commander = (modules / "src/commander.c").read_text()
    rpyt = (modules / "src/crtp_commander_rpyt.c").read_text()
    callback = (modules / "src/crtp_commander.c").read_text()
    header = (modules / "interface/commander.h").read_text()
    config = (base / "main/Kconfig.projbuild").read_text()
    patched = "CONFIG_XS_LINK_LEVEL_MS" in header
    if patched:
        level = int(re.search(r"config XS_LINK_LEVEL_MS.*?default (\d+)", config, re.S)[1])
        stop = int(re.search(r"config XS_LINK_STOP_MS.*?default (\d+)", config, re.S)[1])
    else:
        level = int(re.search(r"TIMEOUT_STABILIZE\s+M2T\((\d+)\)", header)[1])
        stop = int(re.search(r"TIMEOUT_SHUTDOWN\s+M2T\((\d+)\)", header)[1])
    code = PREAMBLE + f"\n#define COMMANDER_WDT_TIMEOUT_STABILIZE {level}u\n#define COMMANDER_WDT_TIMEOUT_SHUTDOWN {stop}u\n"
    code += r'''
#define ASSERT(x) check(x)
#define COMMANDER_PRIORITY_DISABLE 0
#define COMMANDER_PRIORITY_CRTP 1
#define DEFAULT_YAW_MODE XMODE
enum Mode { modeDisable,modeAbs,modeVelocity };
struct V3 { float x=0,y=0,z=0; };
struct Att { float roll=0,pitch=0,yaw=0; };
struct setpoint_t {
 uint32_t timestamp=0; float thrust=0;
 struct { Mode x=modeDisable,y=modeDisable,z=modeDisable,roll=modeDisable,pitch=modeDisable,yaw=modeDisable; } mode;
 Att attitude,attitudeRate; V3 velocity,position; bool velocity_body=false;
};
struct state_t { int dummy=0; };
struct CRTPPacket { uint8_t size=0,port=0,channel=0; uint8_t data[30]={}; };
using BaseType_t=int;
const int pdTRUE=1;
const int setpointQueue=1,priorityQueue=2,priorityDisable=0;
uint32_t nowTick=1000,lastUpdate=0;
int activePriority=0;
setpoint_t queued;
const setpoint_t nullSetpoint;
state_t lastState;
bool enableHighLevel=false;
uint32_t xTaskGetTickCount(){return nowTick;}
int xQueuePeek(int q,void *dest,int){ if(q==1)memcpy(dest,&queued,sizeof(queued));else memcpy(dest,&activePriority,sizeof(activePriority)); return pdTRUE; }
int xQueueOverwrite(int q,const void *src){if(q==1)memcpy(&queued,src,sizeof(queued));else memcpy(&activePriority,src,sizeof(activePriority)); return pdTRUE;}
void crtpCommanderHighLevelGetSetpoint(setpoint_t*,const state_t*){}
bool crtpCommanderHighLevelIsStopped(){return true;}
void crtpCommanderHighLevelStop(){}
int commanderGetActivePriority(){return activePriority;}
enum {CRTP_PORT_SETPOINT=3,CRTP_PORT_SETPOINT_GENERIC=7,SET_SETPOINT_CHANNEL=0,META_COMMAND_CHANNEL=1};
void crtpCommanderGenericDecodeSetpoint(setpoint_t*,CRTPPacket*){}
using Decoder=void(*)(const void*,size_t);
const int nMetaCommands=1;
Decoder metaCommandDecoders[1]={nullptr};
'''
    code += rpyt[rpyt.index("#define MIN_THRUST"):rpyt.index("/**\n * Set flight mode")]
    for name in ("rotateYaw", "yawModeUpdate", "crtpCommanderRpytDecodeSetpoint"):
        code += "\n" + function(rpyt, name)
    for name in ("commanderSetSetpoint", "commanderGetSetpoint"):
        code += "\n" + function(commander, name)
    code += "\n" + function(callback, "commanderCrtpCB")
    code += r'''
void input(uint16_t thrust,float roll=12,float pitch=-8,float yaw=17,uint8_t size=14) {
 CRTPPacket packet; packet.size=size; packet.port=CRTP_PORT_SETPOINT;
 CommanderCrtpLegacyValues values{roll,pitch,yaw,thrust};
 memcpy(packet.data,&values,sizeof(values)); commanderCrtpCB(&packet);
}
int main(){
 state_t state; setpoint_t out;
 input(30000); check(queued.thrust==0); // locked on startup
 input(0); check(queued.thrust==0);
 input(30000); check(queued.thrust==30000); check(queued.attitudeRate.yaw==-17);
 input(65535); check(queued.thrust==60000);
 input(999); check(queued.thrust==0);
 input(30000);
 nowTick=1000+COMMANDER_WDT_TIMEOUT_STABILIZE; commanderGetSetpoint(&out,&state);
 check(out.attitude.roll==12 && out.thrust==30000);
 nowTick++; commanderGetSetpoint(&out,&state);
 check(out.attitude.roll==0 && out.attitude.pitch==0 && out.attitudeRate.yaw==0);
 check(out.thrust==30000 && activePriority==0);
 nowTick=1000+COMMANDER_WDT_TIMEOUT_SHUTDOWN; commanderGetSetpoint(&out,&state);
 check(out.thrust==30000);
 nowTick++; commanderGetSetpoint(&out,&state); check(out.thrust==0);
 input(30000); check(queued.thrust==0); // nonzero reconnect stays locked
 input(0); input(30000); check(queued.thrust==30000);
 // Unsigned tick subtraction remains valid across uint32_t wraparound.
 queued.timestamp=0xffffff00u; nowTick=queued.timestamp+COMMANDER_WDT_TIMEOUT_SHUTDOWN+1;
 commanderGetSetpoint(&out,&state); check(out.thrust==0);
'''
    if patched:
        code += r'''
 input(0); input(30000); auto saved=queued.timestamp;
 for(int length=0;length<=30;length++) {if(length==14)continue; nowTick++;input(50000,12,-8,17,length);check(queued.timestamp==saved && queued.thrust==30000);}
 for(int axis=0;axis<3;axis++) {
   float bound=axis==2?360.0f:45.0f;
   float invalid[5]={NAN,INFINITY,-INFINITY,bound+1,-bound-1};
   for(float bad:invalid) {float axes[3]={0,0,0};axes[axis]=bad;nowTick++;input(30000,axes[0],axes[1],axes[2]);check(queued.timestamp==saved);}
 }
 nowTick=queued.timestamp+COMMANDER_WDT_TIMEOUT_SHUTDOWN+1;
 commanderGetSetpoint(&out,&state);check(out.thrust==0); // malformed input cannot keep motors alive
 input(0);
 for(int axis=0;axis<3;axis++)for(int sign=-1;sign<=1;sign+=2) {
   float axes[3]={0,0,0};axes[axis]=sign*(axis==2?360.0f:45.0f);nowTick++;input(30000,axes[0],axes[1],axes[2]);check(queued.timestamp==nowTick && queued.thrust==30000);
 }
'''
    code += '\nprintf("%d actual-source assertions passed",checks);return 0;}\n'
    result = compile_run(code, "esp_control")
    wifi = (base / "components/drivers/general/wifi/wifi_esp32.c").read_text()
    link = (base / "components/core/crazyflie/hal/src/wifilink.c").read_text()
    if patched:
        # Execute the exact patched bounds expression across the UDP recv range.
        guard = re.search(r"else if \((len < 2[^\n]+)\) \{", wifi)[1]
        bounds_code = PREAMBLE + "\n#define CRTP_MAX_DATA_SIZE 30\nint main(){\n"
        bounds_code += f"for(int len=0;len<128;len++){{bool reject=({guard}); check(reject==(len<2 || len>32));}}\n"
        bounds_code += 'printf("%d UDP boundary assertions passed",checks);}\n'
        boundary_result = compile_run(bounds_code,"udp_bounds")
        assert "wifiIn.size > sizeof(p.raw)" in link
        assert '#define MAX_STA_CONN (1)' in wifi
        assert 'WIFI_AUTH_WPA2_PSK' in wifi
        assert 'CONFIG_XS_WIFI_PASSWORD' in wifi
    else:
        boundary_result = "not patched; stock bounds defects recorded in audit"
    return {"source":str(root), "patched":patched, "level_ms":level,"stop_ms":stop,
            "control":result,"udp_bounds":boundary_result}


def original_test(root):
    source = (root / "NRF24_RX.cpp").read_text()
    config = (root / "config.h").read_text()
    code=PREAMBLE+r'''
using byte=uint8_t;
enum {ROLL,PITCH,YAW,THROTTLE,AUX1,AUX2};
int16_t nrf24_rcData[8]={};
struct RF24Data { byte throttle,yaw,pitch,roll,AUX1,AUX2,switches; } MyData, received;
struct RF24AckPayload {float lat,lon;int16_t heading,pitch,roll;int32_t alt;byte flags;} nrf24AckPayload;
struct {int16_t heading=0,angle[3]={};} att;
struct {int32_t EstAlt=0;} alt;
uint8_t f=0;
unsigned long nowMS=0;
unsigned long millis(){return nowMS;}
long map(long x,long a,long b,long c,long d){return (x-a)*(d-c)/(b-a)+c;}
struct Radio {bool pending=false;bool available(){return pending;} void writeAckPayload(int,void*,size_t){} void read(void* p,size_t n){memcpy(p,&received,n);pending=false;}} radio;
'''
    for name in ("resetRF24Data","NRF24_Read_RC"):
        code += "\n"+function(source,name)
    code += r'''
int main(){
 resetRF24Data();NRF24_Read_RC();check(nrf24_rcData[THROTTLE]==2000);
 nowMS=500;received={255,128,128,128,0,0,0};radio.pending=true;NRF24_Read_RC();check(nrf24_rcData[THROTTLE]==1000);
 nowMS=1500;NRF24_Read_RC();check(nrf24_rcData[THROTTLE]==1000);
 nowMS=1501;NRF24_Read_RC();check(nrf24_rcData[THROTTLE]==2000);
 printf("%d assertions reproduced the upstream full-throttle timeout defect",checks);
}
'''
    assert not re.search(r"^\s*#define FAILSAFE\s*(?://|$)",config,re.M)
    assert not re.search(r"^\s*#define VBAT\s*(?://|$)",config,re.M)
    return {"source":str(root),"result":compile_run(code,"original_receiver"),
            "sha256_NRF24_RX_cpp":hashlib.sha256((root/"NRF24_RX.cpp").read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--esp-source",type=Path,required=True)
    parser.add_argument("--original-source",type=Path)
    args=parser.parse_args()
    report={"scope":"host regression only; no hardware attached", "esp":esp_test(args.esp_source)}
    if args.original_source:
        report["original"]=original_test(args.original_source)
    print(json.dumps(report,indent=2))
