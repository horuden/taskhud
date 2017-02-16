""" ---------------------------------------------------------------------------

    cwrapper.py - Implementation for CursesHud class

    Copyright 2017, John Ferguson

    Licensed under GPLv3, see LICENSE for full details

--------------------------------------------------------------------------- """

import curses

class CursesHud:
    """
    Object that accepts dictionaries representing data records.

    Records are parsed dynamically, so there's no need to configure column
    names ahead of time. Columns can be removed from display, and moved to
    the extended info panel at the bottom by calling set_extra_info().

    To modify record values, translating them to user readable values, call
    set_translation().

    Column widths are initially set to the size of the largest record value's
    length (or the column heading if longer). If the total of displayed column
    widths exceeds available columns in the terminal, 1 column width is
    subtracted from the largest column iteratively until all columns will fit.

    Any column headings/values which are truncated are suffixed by "..."
    """
    def __init__(self, screen):
        """
        screen: curses screen object
        """
        # ncurses screen object
        self.screen = screen
        self.screen.nodelay(True)   # self.screen.getch(), non-blocking

        # Column titles (keys in self.records)
        self.columns = []

        # Key to sort records by
        self.sort_key = None

        # Unique key for records used to disambiguate when records change
        # Note: if value isn't set before adding records, the first key of
        #       the first record becomes the unique key
        self.unique_key = None

        # keys in self.records that should be displayed in bottom pane
        self.extra_info_keys = []

        # Records to display in centre pane
        self.records = []

        # keys - key name from records
        # values - function accepting record value, returns string
        # Used to generically convert from data format to display format
        self.translations = {}

        # index in self.records that centre pane items start listing from
        self.scrollpos = 0

        # index from 0 of displayed items in centre pane that user has
        # selected with arrow keys
        self.selectpos = 0

        # height of bottom panel (for extended info display)
        self.bottom_panel_height = 4

    def set_unique_key(self, key):
        """
        set the unique key to disambiguate when records are updated
        """
        self.unique_key = key

    def set_sort_key(self, key):
        """
        set the key used to sort records after insertion
        """
        self.sort_key = key

    def set_extra_info(self, key):
        """
        set a key in records to be displayed in bottom panel rather than
        main display
        """
        if key in self.columns:
            self.columns.remove(key)
            self.extra_info_keys += [key]

    def set_translation(self, key, func):
        """
        Set callback which translates raw record values keyed by `key` by
        passing the raw value to `func`, which yields the display formatted
        string.
        """
        self.translations[key] = func

    def _get_column_widths(self):
        """
        returns a dict keyed by column name, values are column widths
        """
        column_widths = {}

        # Calculate widths for columns
        # TODO: cache these values if records don't change between renders
        for column in self.columns:
            record_max_width = 0

            for record in self.records:
                if column in record:
                    r_value = record[column]
                    if column in self.translations:
                        r_value = self.translations[column](r_value)
                    else:
                        r_value = str(r_value)
                    
                    record_max_width = max(record_max_width, len(r_value))

            record_max_width += 3

            # len(column) + 3:
            #   len(column): space for column header
            #   +2: left border + space
            #   +1: space on right of header
            column_width = max(record_max_width, len(column) + 3)

            column_widths[column] = column_width

        # Shrink columns until all fits on screen
        # TODO: handling when there's too many columns to render happily
        if sum(column_widths.values()) >= curses.COLS:
            while sum(column_widths.values()) >= curses.COLS:
                key_largest = max(column_widths, key=column_widths.get)
                column_widths[key_largest] -= 1

        return column_widths

    def _render_title(self):
        """
        rendering of title bar on first line (space to display modal info,
        and even keybinding hints)
        """
        title = "{title bar placeholder}"
        title_bar = title + (" " * (curses.COLS - len(title)))
        self.screen.addstr(0,0, title_bar, curses.A_REVERSE)

    def _render_headers(self, start_line=1):
        """
        rendering of headers (3 lines tall, 2 lines header, 1 line bottom
        border.
        """
        pass

    def render(self):
        # Render title bar (placeholder for now)
        self._render_title()

        # TODO: need to apply translation to raw values
        # TODO: break this out into separate function, main panel as well
        # Render bottom panel first
        self.screen.addstr(curses.LINES - self.bottom_panel_height, 0, "─" * curses.COLS)
        for i in range(curses.LINES - self.bottom_panel_height + 1, curses.LINES):
            self.screen.addstr(i, 0, " " * (curses.COLS - 1))

        active_index = self.selectpos
        active_record = self.records[active_index]

        col_acc = 0
        line_acc = 0
        for field in self.extra_info_keys:
            if field not in active_record:
                continue

            st = "{}: {}, ".format(field, active_record[field])
            if col_acc + len(st) >= curses.COLS:
                col_acc = 0
                line_acc += 1

            self.screen.addstr(curses.LINES - self.bottom_panel_height + 1 + line_acc, col_acc, st)
            col_acc += len(st)


        #----------------------------------------------------------------------

        # Then, render the main view

        h_start = 1

        column_widths = self._get_column_widths()
        sum_column_widths = sum([column_widths[c] for c in column_widths])

        # utility function to get first screen column for heading/field
        # based on column name/key
        def column_start(column_name):
            name_index = self.columns.index(column_name)
            col_start = \
                sum([column_widths[c] for c in self.columns[0:name_index]])

            return col_start

        # In case columns change between renders, clearing the first row
        # will ensure that no leftover garbage is only partially drawn over
        self.screen.addstr(h_start,0, " " * curses.COLS)
        self.screen.addstr(h_start + 1,0, " " * curses.COLS)
        
        # draw column headings
        for n, column in enumerate(self.columns):

            col_start = column_start(column)
            col_width = column_widths[column]
            self.screen.addstr(h_start, col_start, "│")
            self.screen.addstr(h_start + 1, col_start, "│")
            string = column
            truncated = string if len(string) < (column_widths[column] - 2) else string[:column_widths[column] - 6] + "..."
            self.screen.addstr(h_start + 1, col_start + 2, truncated)
            self.screen.addstr(h_start + 2, col_start, "┴" + ("─" * (col_width - 1)) )

            # Debug: show column widths with marker
            #self.screen.addstr(2 + (n % 2), col_start, "x" * col_width)
        # add left and right edge of column headings
        self.screen.addstr(h_start + 2, 0, "└")
        self.screen.addstr(h_start, sum_column_widths, "│")
        self.screen.addstr(h_start + 1, sum_column_widths, "│")
        self.screen.addstr(h_start + 2, sum_column_widths, "┘")

        # display records
        slice_start = self.scrollpos
        slice_end = self.scrollpos + curses.LINES - 3 - self.bottom_panel_height
        record_slice = self.records[slice_start:slice_end]
        for nr, record in enumerate(record_slice):
            attr = 0

            if nr + slice_start == self.selectpos:
                attr = curses.A_REVERSE
            else:
                attr = curses.A_NORMAL
            self.screen.addstr(h_start + 3 +nr, 0, " " * curses.COLS, attr)

            for n, column in enumerate(self.columns):
                if column not in record:
                    continue

                col_start = column_start(column)

                value = record[column]
                if column in self.translations:
                    value = self.translations[column](value)

                string = str(value)
                truncated = string if len(string) < (column_widths[column] - 2) else string[:column_widths[column] - 6] + "..."
                self.screen.addstr(h_start + 3 + nr, col_start + 2, truncated, attr)

        # draw latest changes to screen
        self.screen.refresh()

    def add_column(self, name):
        """
        Add a column to the HUD
        """
        self.columns += [name]
    
    def add_record(self, records):
        """
        add records to the display, will add columns as needed. `record` is
        a dictionary, or a list of dictionaries.
        """
        if type(records) is not list:
            records = [records]

        # automatically set unique key if none is set by this point
        if self.unique_key is None:
            self.unique_key = list(records[0].keys())[0]

        # verify that all unique keys are unique for this record set
        unique_keys = []
        for record in records:
            if record[self.unique_key] not in unique_keys:
                unique_keys += [record[self.unique_key]]
            else:
                raise Exception("duplicate records with same unique key")

        for record in records:
            # If record already exists, skip it
            if record in self.records:
                continue

            # If an existing record has the same unique key, then the record
            # has been updated, and we will replace it
            replaced = False
            for n, check in enumerate(self.records):
                if check[self.unique_key] == record[self.unique_key]:
                    self.records[n] = record
                    replaced = True
                    break

            # TODO: need hook to remove columns when no records in the database
            #       have those keys
            # see if new columns are needed to support this record
            for k in record.keys():
                if (k not in self.columns) and (k not in self.extra_info_keys):
                    self.add_column(k)

            if replaced:
                # Old record updated, any new columns added above
                continue
            else:
                # This is a completely new record with new unique key
                self.records += [record]

        # Finally, sort records by appropriate key
        if self.sort_key is not None:
            self.records.sort(key=lambda R: R[self.sort_key])

    def mainloop(self):
        """
        Called after HUD has been set up. Handles rendering and user input.
        """
        # Disable cursor display by default
        curses.curs_set(0)

        # Display initial state
        self.render()

        while True:
            # Render before fetching input
            self.render()

            # note: call is non-blocking, per __init__ calling nodelay(True)
            c = self.screen.getch()

            if c == curses.KEY_RESIZE:
                # Terminal has been resized

                # must be called so that curses.LINES, curses.COLS will change
                curses.update_lines_cols()

                # in case old data won't be redrawn after resize
                self.screen.clear()

            if c == curses.KEY_UP:
                # Move up as far as the 0th record
                self.selectpos = max(self.selectpos - 1, 0)
                if self.selectpos < self.scrollpos:
                    # Handle scrolling if we were at the first record on screen
                    self.scrollpos -= 1
                    
            if c == curses.KEY_DOWN:
                # Move down as far as the Nth record
                self.selectpos = min(self.selectpos + 1, len(self.records) - 1)
                if self.selectpos >= (self.scrollpos + curses.LINES - 2 - self.bottom_panel_height) :
                    # Handle scrolling if we were at the last record on screen
                    self.scrollpos += 1

