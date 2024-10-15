# Gearsim

Gearsim is a PLC utilizing [Zeugwerk Framewerk](https://doc.zeugwerk.dev). This demo application showcases how to use [Units](https://doc.zeugwerk.dev/userguide/overview/overview_unit.html) and [Axes](https://doc.zeugwerk.dev/userguide/overview/overview_equipment.html) to control two indivual gears, which can be moved relative to each other. A python visualization provides a visual representation of real-time control and collision detection.

Note that the demo does not implement an accurate algorithm for synchronizing gears, but instead it provides the foundation for exploring and building upon. We encourage you to experiment and improve the implementation. This demo serves as a starting point for learning and customization, so feel free to play around and make it your own!

<div style="display: flex; justify-content: space-between;">
<img src="/demo.gif"/>
</div>

## Requirements

To run this application, ensure you have the following installed:

- [TwinCAT]() >= 4024.xx
- [Zeugwerk Development Kit](https://doc.zeugwerk.dev/) >= 1.6
- Python 3.x (We recommend [Miniconda](https://docs.anaconda.com/miniconda/))


## Visualization

To run the Visualization in Windows a python distribution has to be installed (Anaconda or Miniconda is recommended).
With an installed python distribution, execute the following commands in the `Visualization` folder to prepare a virtual environment for python and install all requirements

```
pip install virtualenv
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Activate the PLC and run the Visualization with 

```
python main.py
```
