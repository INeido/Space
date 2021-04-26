# Space


Doesn't do much. Just some bodies flying around in the void.

## Settings

| Name | Description | Standard Value |
| ------ | ------ | ------ |
| FPS | Pretty self explanatory, isn't it? | 120 |
| drag | "Air"-Drag, but in space | 0.000001 |
| coll_loss | Loss of speed on collision | 0.000001 |
| res_x | Changes the screen width | 1920 |
| res_y | Do I have to tell you? | 1080 |
| zoom_factor | Zoooooooom | 0.98 |

## Switches

| Name | Description |
| ------ | ------ |
| trace | Enables cool effect |
| edges | If enabled, bodies can't escape screen |
| gravity | The thing with the apple |
| collision_color | Bodies change colors on collision |

## Controls

| Button | Description |
| ------ | ------ |
| ESC | Closes game |
| E | Resets bodies |
| S | Toggles between **Insert** and **Focus** mode |
| Left Click | Follows body when clicked (Focus) |
| A & D | Switch between bodies (Focus) |
| Left Click | Gravitational pull at cursor (Insert) |
| Right Click | Gravitational push at cursor (Insert) |
| Middle Click | Drag screen (Insert) |

![](https://github.com/INeido/Space/blob/main/img/gif1.gif)

## Examples

Kinda stable orbit with 3 bodies
```
bodies.append(Body(p=(0, 300), v=(3, 0), r=5, c=white))
bodies.append(Body(p=(0 + 150, 200), v=(3, 0), r=5, c=white))
bodies.append(Body(p=(0, 0), r=75))
```

Not really stable orbit with 2 bodies
```
bodies.append(Body(p=(100, - 100), v=(3, 2), r=25, c=white))
bodies.append(Body(p=(0, 0), r=50))
```

2 bodies on collision course
```
bodies.append(Body(p=(-600, 0), r=50, v=(3, 0)))
bodies.append(Body(p=(600, 0), r=50, v=(-3, 0)))
```

Create any amount of random bodies defined in **count**. (Don't recommend more than 50)
```
count = 10

rand = random.choices(population=[["5"], ["10"], ["15"], ["20"], ["30"]],
                      weights=[0.35, 0.30, 0.20, 0.1, 0.05],
                      k=count)

for x in range(count):
    bodies.append(Body(p=(random.randint(-res_x / 2, res_x / 2),
                          random.randint(-res_y / 2, res_y / 2)),
                       v=(random.randint(-5, 5),
                          random.randint(-5, 5)),
                       r=int(int(''.join(rand[x]))),
                       c=white))
```

You can past these into the **reset** function.

![](https://github.com/INeido/Space/blob/main/img/gif2.gif)
