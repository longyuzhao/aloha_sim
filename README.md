# Aloha Sim

<a href="#"><img alt="A banner with the title: Aloha Sim" src="media/banner.png" width="100%"></a>

Aloha Sim is a python library that defines the sim environment for the Aloha
robot. It includes a collection of tasks for robot learning and evaluation.

## Installation

Install with pip:

```bash
# create a virtual environment and pip install
pip install -e .
```

**OR** run directly with uv:

```bash
pip install uv
uv run <script>.py
```

Tell mujoco which backend to use, otherwise the simulation will be very slow

```bash
export MUJOCO_GL='egl'
```

## Viewer

Interact with the scene without a policy:

```bash
python aloha_sim/viewer.py --policy=no_policy --task_name=HandOverBanana
```

## Tests

```bash
# individual tests
python aloha_sim/tasks/test/aloha2_task_test.py
python aloha_sim/tasks/test/hand_over_test.py
...

# all tests
python -m unittest discover aloha_sim/tasks/test '*_test.py'
```
## Inference
⚠️ **For Gemini Robotics Trusted Testers Only**

Inference with Gemini Robotics models is intended for
Trusted Testers. If you are not a Trusted Tester, sign up
[here](https://deepmind.google/models/gemini-robotics/).

Follow our [SDK documentation](https://github.com/google-deepmind/gemini-robotics-sdk)
to serve the model. The **same model** used for real-world evaluations can be
directly applied in the simulation environment.

Here is a video walkthrough:

https://github.com/google-deepmind/aloha_sim/tree/main/media/sim_eval_walkthrough.mp4

### Interactive Rollouts
Start the viewer with a chosen task:

```bash
# defaut task: "put the banana in the bowl"
python aloha_sim/viewer.py

# "remove the cap from the marker"
python aloha_sim/viewer.py --task_name=MarkerRemoveLid

# "place the can opener in the left compartment of the caddy"
python aloha_sim/viewer.py --task_name=ToolsPlaceCanOpenerInLeftCompartment
...
```

Checkout [task_suite.py](aloha_sim/task_suite.py#L42) for the list of all tasks
available.

You can use the viewer to pause/resume the environment,
interact with the objects, and enter new instructions for the robot

```
Instructions for using the viewer:

- shift + 'i' = enter new instruction
- space bar = pause/resume.
- backspace = reset environment.
- mouse right moves the camera
- mouse left rotates the camera
- double-click to select an object

When the environment is not running:

- ctrl + mouse left rotates a selected object
- ctrl + mouse right moves a selected object

When the environment is running:

- ctrl + mouse left applies torque to an object
- ctrl + mouse right applies force to an object
```

### Eval
```bash
python aloha_sim/run_eval.py
```

Runs N evaluation episodes for all tasks and save videos
in `/tmp/`.

## Tips

- If the environment stepping is very slow, check that you are using the right
backend, e.g. `MUJOCO_GL='egl'`
- Tasks with deformable objects like `DesktopWrapHeadphone` and
`TowelFoldInHalf` are slow to simulate and interact directly with `viewer.py`.

## Note
This is not an officially supported Google product.

