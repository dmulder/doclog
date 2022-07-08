#!/usr/bin/python3
import os, os.path, pickle, curses, curses.textpad, traceback, argparse, signal

def stop(signal, frame):
    exit(0)

signal.signal(signal.SIGINT, stop)

class DocLog:
    def __init__(self, logfile):
        self.obj = None
        self.oses = None
        self.apps = None
        self.app_objs = None
        if logfile:
            self.logfile = logfile
        else:
            self.logfile = '~/.config/doclog/logs'

    def __enter__(self):
        if os.path.exists(os.path.expanduser(self.logfile)):
            try:
                (self.obj, self.oses, self.apps, self.app_objs) = pickle.load(open(os.path.expanduser(self.logfile), 'rb'))
            except:
                (self.obj, self.oses) = pickle.load(open(os.path.expanduser(self.logfile), 'rb'))
        else:
            self.obj = {}
            self.oses = []
            self.app_objs = {}
            self.apps = []
        return self

    def __exit__(self, type, value, traceback):
        if not os.path.exists(os.path.dirname(os.path.expanduser(self.logfile))):
            os.mkdir(os.path.dirname(os.path.expanduser(self.logfile)))
        pickle.dump((self.obj, self.oses, self.apps, self.app_objs), open(os.path.expanduser(self.logfile), 'wb'))

    def appendOS(self, os):
        self.oses.append(os)

    def osList(self):
        return self.oses

    def categoryList(self, os):
        return [k for k, v in self.obj.items() if os in v.keys()]

    def categoryAppList(self, app):
        return [k for k, v in self.app_objs.items() if app in v.keys()]

    def appendCategory(self, category):
        self.obj[category] = {}

    def appendAppCategory(self, category):
        self.app_objs[category] = {}

    def appendApp(self, app):
        self.apps.append(app)

    def appList(self):
        return self.apps

    def retrieveDocument(self, os, category):
        if os in self.obj[category]:
            return self.obj[category][os]
        else:
            return ''

    def retrieveAppDocument(self, app, category):
        if app in self.app_objs[category]:
            return self.app_objs[category][app]
        else:
            return ''

    def saveDocument(self, os, category, text):
        self.obj[category][os] = text

    def saveAppDocument(self, app, category, text):
        self.app_objs[category][app] = text

class DocLogUI:
    def __init__(self, doclog):
        self.doclog = doclog
        self.screen = None
        self.os = None
        self.category = None

    def __enter__(self):
        self.screen = curses.initscr()
        curses.cbreak()
        self.screen.keypad(1)
        return self

    def __exit__(self, type, value, traceback):
        self.screen.keypad(0)
        curses.nocbreak()
        curses.endwin()

    def main(self):
        self.section = self.__section_prompt()
        if self.section == 'OS Specific':
            self.screen.clear()
            self.screen.addstr(1, 2, 'DocLog')
            self.screen.refresh()
            self.os = self.__os_prompt()
            self.screen.clear()
            self.category = self.__category_prompt()
            self.screen.clear()
            self.__text_box(self.doclog.retrieveDocument(self.os, self.category))
        elif self.section == 'General':
            self.screen.clear()
            self.app = self.__application_prompt()
            self.app_category = self.__app_category_prompt()
            self.screen.clear()
            self.__app_text_box(self.doclog.retrieveAppDocument(self.app, self.app_category))

    def __application_prompt(self):
        self.screen.clear()
        self.screen.addstr(1, 2, 'DocLog')
        if len(self.doclog.appList()) == 0:
            self.screen.addstr(2, 2, 'You have no Applications logged, add one now: ')
            self.screen.refresh()
            self.doclog.appendApp(self.screen.getstr(2, 48).decode())
            return self.doclog.appList()[0]
        else:
            apps = self.doclog.appList()
            for i in range(0, len(apps)):
                self.screen.addstr(i+4, 2, '%d: %s' % (i, apps[i]))
            self.screen.refresh()
            i+=1
            selection = -1
            self.screen.addstr(i+5, 2, 'Select an Application, or %d to add an Application: ' % i)
            while selection < 0 or selection > i:
                try:
                    selection = int(self.screen.getstr(i+5, len('Select an Application, or %d to add an Application: ' % i)+2))
                except:
                    pass
            if selection == i:
                self.screen.addstr(i+5, 2, 'Application name: '+' '*40)
                self.doclog.appendApp(self.screen.getstr(i+5, 11).decode())
            return self.doclog.appList()[selection]

    def __app_category_prompt(self):
        self.screen.clear()
        self.screen.addstr(1, 2, 'DocLog')
        self.screen.addstr(2, 2, self.app)
        self.screen.addstr(3, 2, 'Select a Category')

        if len(self.doclog.categoryAppList(self.app)) == 0:
            self.screen.addstr(5, 2, 'You have no categories logged, add one now: ')
            self.screen.refresh()
            self.doclog.appendCategory(self.screen.getstr(5, 46).decode())
            return self.doclog.categoryAppList(self.app)[0]
        else:
            i = 0
            categories = self.doclog.categoryAppList(self.app)
            for i in range(0, len(categories)):
                self.screen.addstr(i+5, 2, '%d: %s' % (i, categories[i]))
            self.screen.refresh()
            i+=1
            selection = -1
            self.screen.addstr(i+6, 2, 'Select a category, or %d to add one: ' % i)
            while selection < 0 or selection > i:
                try:
                    selection = int(self.screen.getstr(i+6, len('Select a category, or %d to add one: ' % i)+2))
                except:
                    pass
            selected_text = ''
            if selection == i:
                self.screen.addstr(i+6, 2, 'Category name: '+' '*40)
                selected_text = self.screen.getstr(i+6, 17).decode()
                self.doclog.appendAppCategory(selected_text)
            else:
                selected_text = self.doclog.categoryAppList(self.app)[selection]
            return selected_text

    def __section_prompt(self):
        self.screen.addstr(1, 2, 'DocLog')
        categories = ['OS Specific', 'General']
        for i in range(0, len(categories)):
            self.screen.addstr(i+5, 2, '%d: %s' % (i, categories[i]))
        self.screen.refresh()
        i+=1
        selection = -1
        self.screen.addstr(i+6, 2, 'Select a section: ')
        while selection < 0 or selection > i:
            try:
                selection = int(self.screen.getstr(i+6, len('Select a section: ')+2))
            except:
                pass
        selected_text = ''
        selected_text = categories[selection]
        return selected_text

    def __text_box(self, intext):
        self.screen.addstr(1, 2, 'DocLog')
        self.screen.addstr(2, 2, self.os)
        self.screen.addstr(3, 2, self.category)
        if not intext:
            self.doclog.saveDocument(self.os, self.category, self.__edit_text(intext))
        else:
            outtext = intext.split('\n')
            for i in range(0, len(outtext)):
                self.screen.addstr(5+i, 2, outtext[i])
            self.screen.addstr(40, 2, 'Press \'e\' to edit, \'q\' to quit, or any other key to continue')
            ans = self.screen.getch()
            if ans == 101:
                self.doclog.saveDocument(self.os, self.category, self.__edit_text(intext))
            elif ans == 113:
                return
        self.__text_box(self.doclog.retrieveDocument(self.os, self.category))

    def __app_text_box(self, intext):
        self.screen.addstr(1, 2, 'DocLog')
        self.screen.addstr(2, 2, self.app)
        self.screen.addstr(3, 2, self.app_category)
        if not intext:
            self.doclog.saveAppDocument(self.app, self.app_category, self.__edit_text(intext))
        else:
            outtext = intext.split('\n')
            for i in range(0, len(outtext)):
                self.screen.addstr(5+i, 2, outtext[i])
            self.screen.addstr(40, 2, 'Press \'e\' to edit, \'q\' to quit, or any other key to continue')
            ans = self.screen.getch()
            if ans == 101:
                self.doclog.saveAppDocument(self.app, self.app_category, self.__edit_text(intext))
            elif ans == 113:
                return
        self.__app_text_box(self.doclog.retrieveAppDocument(self.app, self.app_category))

    def __edit_text(self, intext):
        curses.noecho()
        win = curses.newwin(40, 104, 5, 2)
        tb = curses.textpad.Textbox(win)
        self.screen.addstr(44, 2, 'Press Ctrl-G when finished'+' '*40)
        self.screen.refresh()
        for inchar in intext:
            tb.do_command(ord(inchar))
        text = tb.edit()
        self.screen.clear()
        curses.echo()
        return text

    def __os_prompt(self):
        if len(self.doclog.osList()) == 0:
            self.screen.addstr(2, 2, 'You have no OSes logged, add one now: ')
            self.screen.refresh()
            self.doclog.appendOS(self.screen.getstr(2, 40).decode())
            return self.doclog.osList()[0]
        else:
            oses = self.doclog.osList()
            for i in range(0, len(oses)):
                self.screen.addstr(i+4, 2, '%d: %s' % (i, oses[i]))
            self.screen.refresh()
            i+=1
            selection = -1
            self.screen.addstr(i+5, 2, 'Select an OS, or %d to add an OS: ' % i)
            while selection < 0 or selection > i:
                try:
                    selection = int(self.screen.getstr(i+5, len('Select an OS, or %d to add an OS: ' % i)+2))
                except:
                    pass
            if selection == i:
                self.screen.addstr(i+5, 2, 'OS name: '+' '*40)
                self.doclog.appendOS(self.screen.getstr(i+5, 11).decode())
            return self.doclog.osList()[selection]

    def __category_prompt(self):
        self.screen.clear()
        self.screen.addstr(1, 2, 'DocLog')
        self.screen.addstr(2, 2, self.os)
        self.screen.addstr(3, 2, 'Select a Category')

        if len(self.doclog.categoryList(self.os)) == 0:
            self.screen.addstr(5, 2, 'You have no categories logged, add one now: ')
            self.screen.refresh()
            self.doclog.appendCategory(self.screen.getstr(5, 46).decode())
            return self.doclog.categoryList(self.os)[0]
        else:
            categories = self.doclog.categoryList(self.os)
            for i in range(0, len(categories)):
                self.screen.addstr(i+5, 2, '%d: %s' % (i, categories[i]))
            self.screen.refresh()
            i+=1
            selection = -1
            self.screen.addstr(i+6, 2, 'Select a category, or %d to add one: ' % i)
            while selection < 0 or selection > i:
                try:
                    selection = int(self.screen.getstr(i+6, len('Select a category, or %d to add one: ' % i)+2))
                except:
                    pass
            selected_text = ''
            if selection == i:
                self.screen.addstr(i+6, 2, 'Category name: '+' '*40)
                selected_text = self.screen.getstr(i+6, 17).decode()
                self.doclog.appendCategory(selected_text)
            else:
                selected_text = self.doclog.categoryList(self.os)[selection]
            return selected_text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DocLog is a simple tool for storing documents by subject and operating system', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--docfile', help='The location to store/retrieve document logs')
    args = parser.parse_args()

    with DocLog(args.docfile) as doclog, DocLogUI(doclog) as doclogui:
        doclogui.main()

