# TaskHUD

Simple interface to TaskWarrior using `ncurses`

## Objectives

* Configurable, but usable out of the box
* Doesn't require you to memorize loads of keybindings
* Provides extended history and metadata for tasks that the standard JSON
  export interface doesn't provide

## Development Status

### 2017-02-15

* All items from task database displayed
* Everything updates automatically when changes are made from `task`
* All the funky stuff like terminal resize is handled
* Bottom panel to display extra record fields when columns have to be excluded
  from main display for readability
* Automatic translation of ugly looking fields
* Project is slowly turning into two components:
    * Main project (TaskHUD)
    * CursesHud (I've made every effort to keep TaskHUD logic out of it)

![screengrab](https://i.imgur.com/JoIGEIA.png)

