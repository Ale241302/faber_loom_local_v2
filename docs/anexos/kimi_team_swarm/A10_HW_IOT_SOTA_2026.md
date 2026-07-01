## A10_HW_IOT — Hardware embedded / BLE / OTA / device management

### Estado del arte 2026
| Práctica | Líder | Trade-off | Conf |
| Rust+Embassy | STM32/Nordic/ESP32 prod [^156^] | 5-6 sem curva; no cert DO-178C | [HIGH] |
| nRF Connect SDK/Zephyr | Stack oficial Nordic 2026 [^141^][^153^] | Más abstracción que nRF5 legacy | [HIGH] |
| MCUboot+ECDSA firmado | Estándar OTA 2026 [^173^] | Requiere HSM offline claves | [HIGH] |

### Tendencias 2026–2028
| Tendencia | Señal/Ruido | Razón | Conf |
| Rust embedded mainstream | Señal | Cargo+probe-rs listos; adopción real [^145^] | [HIGH] |
| Secure element/TPM en IoT | Señal | CRA+RED exigen state-of-art cifrado [^166^][^170^] | [HIGH] |
| Zephyr único stack Nordic | Señal | nRF5 SDK en mantenimiento [^153^] | [HIGH] |

### Stack/herramientas SOTA top 3
| Herramienta | Uso | Trade-off | LATAM-ready | Conf |
| nRF Connect SDK + MCUboot | BLE+OTA nRF54/nRF52 | Curva Zephyr/Kconfig | Sí, DevZone [^141^] | [HIGH] |
| Memfault | Fleet debug+OTA RTOS | Precio escalable; Zephyr preview [^151^] | Sí, cloud | [MEDIA] |
| probe-rs + cargo-embed | Debug/flasheo Rust | Reemplaza JLink/OpenOCD | Sí, OSS [^145^] | [HIGH] |

### Bloque A — Roles SOTA
| Rol | Seniority | Scope | Sep/Cap | Justificación | Conf |
| Embedded Architect | Staff | Stack OTA seg | Sep | Define MCUboot, BLE [^174^] | [HIGH] |
| Firmware Engineer | Senior | Drivers, sensores, BLE | 2× mín | Zephyr+RTOS+capacitivo [^169^] | [HIGH] |
| RF/BLE Specialist | Senior | Controller, interoperability | Sep | Nordic requiere experto [^141^] | [HIGH] |
| Security Engineer | Senior | Secure boot, claves, CRA | Sep | CRA 2026 obliga reporting [^166^] | [HIGH] |
| HW/PCB Engineer | Senior | ADC, power, DFM | Sep | 1681 sensores, layout [^174^] | [HIGH] |
| Manufacturing/Test | Mid | DFT, EOL, calibración | Sep | Escalado <10k/año | [MEDIA] |

### Bloque B — Competencias transversales
1. **Rust/C interop** — FFI migración gradual; evaluar proyecto STM32H7 [^145^] — [HIGH]
2. **Seguridad firmware** — Secure boot, OTA signed, SBOM; CRA 24h reporte [^166^] — [HIGH]
3. **Devicetree/Zephyr** — Overlays, Kconfig, Partition Manager; obligatorio NCS [^148^] — [HIGH]

### Anti-patterns 2026 + KPIs
| Anti-pattern | Por qué murió | KPI/SLO reemplazo |
| nRF5 SDK legacy | Maintenance mode, sin nRF54 [^153^] | 100% builds NCS/Zephyr by Q3 |
| OTA sin firma | CRA/RED prohíben; MITM/brick [^140^] | 100% ECDSA firmado + rollback |
| Equipo <5 FTE HW/FW | Imposible BLE+OTA+seg+PCB+test [^176^] | 8-10 FTE antes AC-02 gate |
| Biométricos sin cifrado hw | Secure storage mandatory CRA I [^168^] | CryptoCell-310/KMU 100% units |
