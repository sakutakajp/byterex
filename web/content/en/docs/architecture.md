---
title: System Architecture
description: An overview of the hardware and system that will bring recognition, manipulation, and decision-making together in the Byterex household robot.
---

# System Architecture

Built on LeKiwi / LeRobot, Byterex aims to develop **a robot that recognizes, picks up, and sorts laundry**.

## Overview

We plan to combine a robotic arm, cameras, a Raspberry Pi, and an AI accelerator to integrate object recognition, manipulation, and decision-making into a single system.

## Main Hardware

- **Mobile base: LeKiwi** — Moves the robot around.
- **Robotic arm: SO-ARM101** — Picks up and moves laundry.
- **Cameras** — Capture laundry and its surroundings.
- **Raspberry Pi and AI accelerator** — We are exploring a configuration for recognition and control processing.

## Intended Workflow

1. Capture laundry with a camera
2. Recognize the laundry and decide which item to pick up
3. Pick up and sort the item with the robotic arm
