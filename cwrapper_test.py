from cwrapper import CursesHud
from curses import wrapper
import curses


def grabber(s):
    hud = CursesHud(s)

    test_names = ["id", "herby", "a longer one", "derb"]

    hud.add_record(
        {
            "id": 1,
            "glorbness": "such glorb",
            "diatribe": "a smol string",
            "supplemental": "multivitamins"
        }
    )
    hud.add_record(
        {
            "id": 2034,
            "glorbness": "much glorb",
            "diatribe": "a less smol string",
            "supplemental": "well-annotated"
        }        
    )
    hud.add_record(
        {
            "id": 403895,
            "glorbness": "over 9000 glorb",
            "diatribe": "this one's going to go right off the screen, or at least that's the hope be it long enough",
            "supplemental": "more test data",
            "unique-to-one": "hopefully it works"
        }        
    )

    hud.mainloop()

wrapper(grabber)
