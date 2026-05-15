#!/usr/bin/env python3

import json
import yaml
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = REPO_ROOT / "greenhouse_setup" / "greenhouse_config.yaml"
TAGS_PATH = REPO_ROOT / "greenhouse_setup" / "tag_locations.json"
WORLD_PATH = REPO_ROOT / "worlds" / "greenhouse.world"


TABLE_HEIGHT = 0.5
WALL_HEIGHT = 1.2
WALL_THICKNESS = 0.08

# The original tables are only 0.25 m thick.
# For LiDAR-based mapping, slightly thicker collision objects are easier to scan.
MIN_TABLE_SIZE_FOR_SLAM = 0.35


def sanitize_name(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


def box_model(name, x, y, z, sx, sy, sz, color="0.5 0.8 0.5 1"):
    return f"""
    <model name="{sanitize_name(name)}">
      <static>true</static>
      <pose>{x:.3f} {y:.3f} {z:.3f} 0 0 0</pose>
      <link name="link">

        <collision name="collision">
          <geometry>
            <box>
              <size>{sx:.3f} {sy:.3f} {sz:.3f}</size>
            </box>
          </geometry>
        </collision>

        <visual name="visual">
          <geometry>
            <box>
              <size>{sx:.3f} {sy:.3f} {sz:.3f}</size>
            </box>
          </geometry>
          <material>
            <ambient>{color}</ambient>
            <diffuse>{color}</diffuse>
          </material>
        </visual>

      </link>
    </model>
"""


def cylinder_marker(name, x, y, z, radius=0.08, height=0.04, color="1 0 0 1"):
    return f"""
    <model name="{sanitize_name(name)}">
      <static>true</static>
      <pose>{x:.3f} {y:.3f} {z:.3f} 0 0 0</pose>
      <link name="link">

        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>{radius:.3f}</radius>
              <length>{height:.3f}</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>{color}</ambient>
            <diffuse>{color}</diffuse>
          </material>
        </visual>

      </link>
    </model>
"""


def main():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    with open(TAGS_PATH, "r") as f:
        layout = json.load(f)

    width = float(config["visualization"]["greenhouse_width_m"])
    height = float(config["visualization"]["greenhouse_height_m"])

    tables = layout.get("tables", {})
    tags = layout.get("tags", {})

    models = []

    # Floor
    models.append(
        box_model(
            name="greenhouse_floor",
            x=width / 2.0,
            y=height / 2.0,
            z=-0.01,
            sx=width,
            sy=height,
            sz=0.02,
            color="0.75 0.75 0.75 1",
        )
    )

    # Boundary walls
    models.append(
        box_model(
            name="wall_left",
            x=-WALL_THICKNESS / 2.0,
            y=height / 2.0,
            z=WALL_HEIGHT / 2.0,
            sx=WALL_THICKNESS,
            sy=height,
            sz=WALL_HEIGHT,
            color="0.7 0.7 0.7 1",
        )
    )

    models.append(
        box_model(
            name="wall_right",
            x=width + WALL_THICKNESS / 2.0,
            y=height / 2.0,
            z=WALL_HEIGHT / 2.0,
            sx=WALL_THICKNESS,
            sy=height,
            sz=WALL_HEIGHT,
            color="0.7 0.7 0.7 1",
        )
    )

    models.append(
        box_model(
            name="wall_bottom",
            x=width / 2.0,
            y=-WALL_THICKNESS / 2.0,
            z=WALL_HEIGHT / 2.0,
            sx=width,
            sy=WALL_THICKNESS,
            sz=WALL_HEIGHT,
            color="0.7 0.7 0.7 1",
        )
    )

    models.append(
        box_model(
            name="wall_top",
            x=width / 2.0,
            y=height + WALL_THICKNESS / 2.0,
            z=WALL_HEIGHT / 2.0,
            sx=width,
            sy=WALL_THICKNESS,
            sz=WALL_HEIGHT,
            color="0.7 0.7 0.7 1",
        )
    )

    # Tables as physical obstacles
    for table_name, table in tables.items():
        x0 = float(table["x0"])
        y0 = float(table["y0"])
        x1 = float(table["x1"])
        y1 = float(table["y1"])

        center_x = (x0 + x1) / 2.0
        center_y = (y0 + y1) / 2.0

        size_x = abs(x1 - x0)
        size_y = abs(y1 - y0)

        # Make very thin tables slightly thicker for reliable LiDAR mapping.
        size_x = max(size_x, MIN_TABLE_SIZE_FOR_SLAM)
        size_y = max(size_y, MIN_TABLE_SIZE_FOR_SLAM)

        models.append(
            box_model(
                name=table_name,
                x=center_x,
                y=center_y,
                z=TABLE_HEIGHT / 2.0,
                sx=size_x,
                sy=size_y,
                sz=TABLE_HEIGHT,
                color="0.25 0.65 0.25 1",
            )
        )

    # Tag markers as red visual markers
    for tag_name, tag in tags.items():
        x = float(tag["x"])
        y = float(tag["y"])

        models.append(
            cylinder_marker(
                name=tag_name,
                x=x,
                y=y,
                z=TABLE_HEIGHT + 0.05,
                radius=0.08,
                height=0.04,
                color="1 0 0 1",
            )
        )

    world_content = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="greenhouse_world">

    <include>
      <uri>model://sun</uri>
    </include>

    {''.join(models)}

  </world>
</sdf>
"""

    WORLD_PATH.parent.mkdir(parents=True, exist_ok=True)
    WORLD_PATH.write_text(world_content)

    print(f"Generated Gazebo world:")
    print(f"  {WORLD_PATH}")
    print(f"Greenhouse size: {width} m x {height} m")
    print(f"Tables: {len(tables)}")
    print(f"Tags: {len(tags)}")


if __name__ == "__main__":
    main()