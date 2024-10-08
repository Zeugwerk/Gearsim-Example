# Gearsim

Gearsim is a PLC utilizing [Zeugwerk Framewerk](https://doc.zeugwerk.dev). This demo application showcases how to use [Units](https://doc.zeugwerk.dev/userguide/overview/overview_unit.html) and [Axes](https://doc.zeugwerk.dev/userguide/overview/overview_equipment.html) to control indivuals gears, which can be moved relative to each other. A python visualization provides a visual representation of real-time control and collision detection.

In the demo, you can see three gears:

- The **left gear** is the *primary* gear. During the automatic sequence of the machine, this gear rotates at a constant velocity.
- The **upper right gear** tries to match the velocity of the primary gear and occasionally spins at twice the speed. However, this gear is not phase-synchronized with the primary gear—only the velocity is matched. As a result, you can observe crashes in the demo.
- The **lower right gear** exhibits similar behavior to the upper gear, but it uses [Struckig](https://github.com/stefanbesler/struckig) to synchronize the phases. This ensures that the phases of the primary gear and the lower gear are aligned when they move together. The behavior is reminiscent of a flying saw.

<div style="display: flex; justify-content: space-between;">
<img src="/Images/Peek 2024-10-08 21-52.gif"/>
</div>

## Requirements

To run this application, ensure you have the following installed:

- [TwinCAT]() >= 4024.xx
- [Zeugwerk Development Kit](https://doc.zeugwerk.dev/) >= 1.6
- Python 3.x (We recommend [Miniconda](https://docs.anaconda.com/miniconda/))


## Visualization

To run the Visualization in Windows a python distribution has to be installed (Anaconda or Miniconda is recommended).
With an installed python distribution, execute the following commands in the `Visualization` folder to prepare a virtual environment for python and install all requirements

```bash
pip install virtualenv
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Activate the PLC and run the Visualization with 

```bash
python main.py
```

You can use the `Servicepanel`, which is integrated into Zeugwerk Creator to control the PLC.
