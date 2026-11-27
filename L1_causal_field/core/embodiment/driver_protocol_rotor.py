r"""
ELYSIA Phase 3/5 Bridge — Real Hardware & Driver-Translator Protocol Rotor
==========================================================================

Observes the ACTUAL hardware devices & driver protocols on THIS PC (read-only),
reclassifies them into the 5 irreducible Minimal-OS Rotor Translator classes,
and separates:
  - Open / Standard Protocols (0 — directly recreatable in a Minimal UEFI/OS:
    UEFI GOP, USB HID, NVMe/AHCI, PCIe Config, VirtIO, Standard Audio/NIC)
  - Proprietary Vendor Dialects (1 — requires a thin Translator Membrane:
    NVIDIA CUDA proprietary firmware, vendor-specific Wi-Fi/chipset blobs)

Zero fakes, zero hardcoded mock hardware lists.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from typing import Any, Dict, List

try:
    import winreg
except ImportError:
    winreg = None


def _probe_via_winreg(limit: int = 80) -> List[Dict[str, str]]:
    """Fast native Windows registry hardware bus enumeration (PCI, USB, HID, DISPLAY, SCSI)."""
    if winreg is None:
        return []
    buses = [
        ("PCI", "System"),
        ("DISPLAY", "Display"),
        ("HID", "HIDClass"),
        ("USB", "USB"),
        ("SCSI", "DiskDrive"),
        ("USBSTOR", "DiskDrive"),
    ]
    out: List[Dict[str, str]] = []
    seen = set()
    for bus_key, default_cls in buses:
        if len(out) >= limit:
            break
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, rf"SYSTEM\CurrentControlSet\Enum\{bus_key}") as root_k:
                i = 0
                while len(out) < limit:
                    try:
                        dev_id = winreg.EnumKey(root_k, i)
                        i += 1
                    except OSError:
                        break
                    try:
                        with winreg.OpenKey(root_k, dev_id) as dk:
                            inst_id = winreg.EnumKey(dk, 0)
                            with winreg.OpenKey(dk, inst_id) as ik:
                                def _get(val_name: str) -> str:
                                    try:
                                        v, _ = winreg.QueryValueEx(ik, val_name)
                                        return str(v)
                                    except OSError:
                                        return ""
                                desc = _get("FriendlyName") or _get("DeviceDesc")
                                if ";" in desc:
                                    desc = desc.split(";")[-1]
                                pnp_cls = _get("Class") or default_cls
                                mfr = _get("Mfg")
                                if ";" in mfr:
                                    mfr = mfr.split(";")[-1]
                                svc = _get("Service")
                                key_dedup = (desc, pnp_cls, svc)
                                if desc and key_dedup not in seen:
                                    seen.add(key_dedup)
                                    out.append(
                                        {
                                            "name": desc,
                                            "pnp_class": pnp_cls,
                                            "manufacturer": mfr,
                                            "device_id": f"{bus_key}\\{dev_id}",
                                            "service": svc,
                                        }
                                    )
                    except OSError:
                        continue
        except OSError:
            continue
    return out


_PS_HARDWARE_PROBE = r"""
$items = @()
$classes = @('Display','DiskDrive','Keyboard','Mouse','HIDClass','Net','MEDIA','USB','System')
Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue | Where-Object {
  $_.Status -eq 'OK' -and $_.PNPClass -in $classes
} | Select-Object -First 80 Name, PNPClass, Manufacturer, DeviceID, Service | ForEach-Object {
  $items += [PSCustomObject]@{
    name = [string]$_.Name
    pnp_class = [string]$_.PNPClass
    manufacturer = [string]$_.Manufacturer
    device_id = [string]$_.DeviceID
    service = [string]$_.Service
  }
}
$items | ConvertTo-Json -Depth 3 -Compress
"""


def _classify_protocol_openness(pnp_class: str, name: str, mfr: str, dev_id: str, service: str) -> Dict[str, Any]:
    low = f"{name} {mfr} {dev_id} {service}".lower()

    # Map Windows PnP class + real hardware descriptors -> Minimal OS Scale-Rotor Translator category
    if pnp_class in ("Display", "MEDIA") or any(k in low for k in ["geforce", "nvidia", "radeon", "audio", "display", "monitor"]):
        rotor_cat = "표현 로터 통역사 (Display/Audio)"
        standard_spec = "UEFI GOP / DisplayPort-HDMI / HDA Audio"
        eff_class = "Display"
    elif pnp_class == "Net" or any(k in low for k in ["ethernet", "gbe", "wi-fi", "wireless", "network", "lan"]):
        rotor_cat = "세계 접촉 로터 통역사 (NIC/Wi-Fi)"
        standard_spec = "Ethernet IEEE 802.3 / VirtIO-Net"
        eff_class = "Net"
    elif pnp_class in ("Keyboard", "Mouse", "HIDClass", "USB") or any(k in low for k in ["hid", "usb", "keyboard", "mouse"]):
        rotor_cat = "입력 로터 통역사 (HID/USB)"
        standard_spec = "USB HID / xHCI 표준 규약"
        eff_class = "HIDClass"
    elif pnp_class == "DiskDrive" or any(k in low for k in ["nvme", "ssd", "sata", "ahci", "disk", "scsi"]):
        rotor_cat = "지속성 로터 통역사 (NVMe/Block)"
        standard_spec = "NVMe / AHCI / UEFI Block I/O"
        eff_class = "DiskDrive"
    else:
        rotor_cat = "물리·버스 제약 로터 (PCIe/ACPI)"
        standard_spec = "PCIe Config Space / ACPI 표준 테이블"
        eff_class = "System"

    # Distinguish open recreatable standards (0) vs proprietary vendor dialects (1)
    is_proprietary = any(
        k in low
        for k in ["nvidia", "geforce", "nvlddmkm", "realtek", "broadcom", "qualcomm", "mediatek", "razer", "logitech"]
    )
    if is_proprietary and eff_class in ("Display", "Net"):
        protocol_nature = "proprietary_translator_1"
        nature_ko = "제조사 비공개 사투리 (1 · 통역 경계막 필요)"
        minimal_os_path = "기본 입출력은 표준(UEFI GOP/HDA)으로 재창조, 고속 가속(CUDA 등)은 통역 경계 유지"
    else:
        protocol_nature = "open_recreatable_0"
        nature_ko = "개방·표준 프로토콜 (0 · 최소 OS 직접 재창조 가능)"
        minimal_os_path = f"{standard_spec} 기반으로 최소 로터 OS에서 직접 구현 가능"

    bus = "PCIe" if dev_id.startswith("PCI\\") else ("USB/HID" if dev_id.startswith(("USB\\", "HID\\")) else ("ACPI" if dev_id.startswith("ACPI\\") else "Storage/Other"))

    return {
        "rotor_translator": rotor_cat,
        "bus": bus,
        "standard_spec": standard_spec,
        "protocol_nature": protocol_nature,
        "nature_ko": nature_ko,
        "minimal_os_path": minimal_os_path,
    }


def observe_driver_protocol_rotors() -> Dict[str, Any]:
    """Queries live PC hardware/drivers and reclassifies them into Scale-Rotor Translators."""
    parsed: List[Dict[str, Any]] = _probe_via_winreg(limit=80)
    if not parsed:
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", _PS_HARDWARE_PROBE],
                capture_output=True,
                text=True,
                timeout=12,
            )
            raw = proc.stdout.strip()
            if proc.returncode != 0 or not raw:
                return {"status": "error", "message": proc.stderr.strip() or "No hardware data returned"}
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                parsed = [parsed]
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    rotors: List[Dict[str, Any]] = []
    by_category: Dict[str, Dict[str, int]] = {}
    open_count = 0
    prop_count = 0

    for item in parsed:
        name = str(item.get("name") or "")
        pnp_class = str(item.get("pnp_class") or "")
        mfr = str(item.get("manufacturer") or "")
        dev_id = str(item.get("device_id") or "")
        service = str(item.get("service") or "")
        if not name:
            continue
        cls = _classify_protocol_openness(pnp_class, name, mfr, dev_id, service)
        if cls["protocol_nature"] == "open_recreatable_0":
            open_count += 1
        else:
            prop_count += 1

        cat = cls["rotor_translator"]
        if cat not in by_category:
            by_category[cat] = {"open_0": 0, "proprietary_1": 0}
        if cls["protocol_nature"] == "open_recreatable_0":
            by_category[cat]["open_0"] += 1
        else:
            by_category[cat]["proprietary_1"] += 1

        rotors.append(
            {
                "name": name,
                "pnp_class": pnp_class,
                "manufacturer": mfr,
                "service": service,
                "device_id_prefix": dev_id[:36],
                **cls,
            }
        )

    return {
        "status": "ok",
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "total_devices_observed": len(rotors),
            "open_recreatable_0": open_count,
            "proprietary_translator_1": prop_count,
            "recreatable_ratio": round(open_count / max(1, len(rotors)), 3),
            "by_rotor_translator": by_category,
        },
        "highlight_proprietary_boundaries": [r for r in rotors if r["protocol_nature"] == "proprietary_translator_1"][:8],
        "highlight_open_recreatable": [r for r in rotors if r["protocol_nature"] == "open_recreatable_0"][:10],
    }


if __name__ == "__main__":
    print(json.dumps(observe_driver_protocol_rotors(), ensure_ascii=False, indent=2))
