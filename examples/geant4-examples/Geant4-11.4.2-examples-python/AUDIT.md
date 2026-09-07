# Geant4 example compatibility audit

- Official CMake targets: 262
- Official GDML files: 144
- Standalone GDML candidates: 143
- Python ports passing: 27
- Python ports failing/timing out: 0

| Python port | Status | Seconds |
|---|---:|---:|
| `advanced/GoldFoilExperiment/gold_foil.py` | passed | 3.794 |
| `advanced/NanoparticleTherapy/brain_tumor.py` | passed | 4.751 |
| `advanced/NanoparticleTherapy/nano_therapy.py` | passed | 4.411 |
| `basic/B1/b1.py` | passed | 1.739 |
| `basic/B2/b2.py` | passed | 1.933 |
| `basic/B3/b3.py` | passed | 1.779 |
| `basic/B4/b4.py` | passed | 2.447 |
| `basic/B5/b5.py` | passed | 2.266 |
| `extended/analysis/AnaEx01/ana_ex01.py` | passed | 2.004 |
| `extended/analysis/AnaEx02/ana_ex02.py` | passed | 1.198 |
| `extended/analysis/AnaEx03/ana_ex03.py` | passed | 1.104 |
| `extended/electromagnetic/TestEm1/test_em1.py` | passed | 1.353 |
| `extended/eventgenerator/HepMC/hepmc.py` | passed | 1.063 |
| `extended/eventgenerator/exgps/exgps.py` | passed | 1.899 |
| `extended/eventgenerator/particleGun/particle_gun.py` | passed | 1.755 |
| `extended/field/field01/field01.py` | passed | 1.364 |
| `extended/field/field02/field02.py` | passed | 0.966 |
| `extended/hadronic/Hadr00/hadr00.py` | passed | 1.949 |
| `extended/medical/GammaTherapy/gamma_therapy.py` | passed | 1.333 |
| `extended/medical/electronScattering/electron_scattering.py` | passed | 1.794 |
| `extended/optical/LXe/lxe.py` | passed | 1.556 |
| `extended/optical/OpNovice/op_novice.py` | passed | 1.399 |
| `extended/optical/wls/wls.py` | passed | 1.367 |
| `extended/parameterisations/Par01/par01.py` | passed | 1.592 |
| `extended/physicslists/factory/factory.py` | passed | 1.134 |
| `extended/radioactivedecay/rdecay01/rdecay01.py` | passed | 1.167 |
| `extended/runAndEvent/RE01/re01.py` | passed | 1.376 |
| `run_gdml.py` | utility |  |

Only entries marked `passed` are validated as runnable Python ports.
