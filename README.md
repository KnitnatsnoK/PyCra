# PyCra : A programmatic game engine made in/for python with beta hardware-accelerated pygame

PyCra is a lightweight, hardware-accelerated game engine built for Python using Pygame. 
It provides a simple yet powerful framework for creating 2D games programmatically.

## Features
- Hardware-accelerated rendering with Pygame
- Project system
- Window Management system
- Customizable scene and entity system
- Event handling and input management (mouse, keyboard, controllers)
- Simple physics and collision detection
- GUI support for in-game interfaces (text boxes, pop-ups, scroll wheels, ...)
- Does NOT support built-in multi-threading yet

## Installation
To install Pycra, clone the repository and run setup.py to install all dependencies:
```bash
git clone https://github.com/KnitnatsnoK/PyCra
cd PyCra/PyCra
python Setup/setup.py
```

## Getting Started
PyCra will always create a main.py file with the necessairy tick()-function for you when creating a project.
You can add anything you want to main.py and it gets run in the beginning of runtime.
A PyCra-game will run the tick()-function every frame, so it's a ```while True:```-replacement.

## Documentation
Check out the full documentation [https://github.com/KnitnatsnoK/PyCra/wiki](https://github.com/KnitnatsnoK/PyCra/wiki).

## License
Pycra is available under a **custom MIT license** with commercial use restrictions. 

If your project generates more than $1,000 in revenue, you must acquire a commercial license.
Contact: [knitnatsnokfeedback@gmail.com](mailto:knitnatsnokfeedback@gmail.com)

## Contributing
Contributions are welcome! Feel free to submit issues or pull requests.
