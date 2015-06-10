# james shubin, 260165643
# my menu system was done with the code and fix software engineering model
# i bet it's just as strong and bug free as anyone elses :P
# on a serious note, it's really solid i think. check the nice features!

#TODO: wherever validation of an add_entry fails, we print error, raise exception and return false.
#	these are all listed here, but obviously they are superfluous, remove either print, raise or both.
import sys
class menu_system:
    """a simple menu system class"""

    def __init__(self, title='menu', prompt='$ '):
        """the constructor"""
        self.nl = '\n'		# pick your favourite newline character '\r\n' for m$ lusers (or '|\n') for fun
        self.prefix = ''	# sandwich the key
        self.postfix = ') '	# close the sandwich
        self.seperator = ''
        # 76 = 80 - (3 + 1)
        # max = default screen char width - (# menu item chars + 1 letter char + 1 end of line space)
        self.maxtextlen = 80 - (len(self.prefix) + len(self.postfix) + 1 + len(self.nl))

        self.title = title	# the menu title
        self.prompt = prompt	# the menu prompt
        self.entries = []	#list of menu items

        self.myout = sys.stdout	# set these if you would like different
        self.myerr = sys.stderr # they need to have a write() method


    def add_entry(self, key, text, sub=None):
        """add entries to our menu:
            key is single A-Z, a-z letter choice, no duplicates
            text is text you want to display
            sub is None for regular function
            sub is lambda function or function for something to happen on press
            if the function returns true, then menu returns,
            otherwise it loops in menu
            sub is a built menu_system class if you want a sub menu to run and return next
            """
        # validation
        if not(type(key) in [type('a')] and type(text) in [type('abc')]):
            self.myerr.write('key and text parameters must be strings' + self.nl)
            raise Exception('key and text parameters must be strings')
            return False

        # empty lines
        if key is '' and text is '':
            temp = {'key': '', 'text': '', 'sub': None}
            self.entries.append(temp)

        elif len(key) != 1 or len(text) > self.maxtextlen:

            self.myerr.write(('key must be one char, text must be max %d' % self.maxtextlen) + self.nl)
            raise Exception('key must be one char, text must be max %d' % self.maxtextlen)
            return False


        elif (ord(key) >= ord('A') and ord(key) <= ord('Z')) or \
             (ord(key) >= ord('a') and ord(key) <= ord('z'))  or \
             (ord(key) >= ord('0') and ord(key) <= ord('9')):

            # check to avoid duplicate keys
            for x in self.entries:
                if x['key'] == key:
                    self.myerr.write('key must be unique to this menu' + self.nl)
                    raise Exception('key must be unique to this menu')
                    return False

            #TODO: we could add truncation of text if it's too long
            temp = {'key': key, 'text': text, 'sub': sub}
            self.entries.append(temp)
            return True # happy

        else:
            self.myerr.write('bad key for menu entry' + self.nl)
            raise Exception('bad key for menu entry')
            return False


    def add_seperator(self):
        self.add_entry('','')

    def run(self, answer=None):
        """runs the menu system, returns selected letter"""
        while True:


            if answer is None:
                sys.stdout.write(self.title + self.nl) # print title
                for x in self.entries:
                    if x['key'] is '':
                        sys.stdout.write(self.prefix + self.seperator + self.nl)
                    else:
                        sys.stdout.write(self.prefix + x['key'] + self.postfix + x['text'] + self.nl)

                try: # do safe/smart prompt
                    answer = '' # safe
                    answer = raw_input(self.prompt)

                except EOFError: #user pressed ^D
                    self.myerr.write('you pressed ^D' + self.nl)
                    return False

                except KeyboardInterrupt:
                    self.myerr.write('you pressed ^C' + self.nl)
                    return False


            #self.myerr.write(('you pressed %s\n' % answer) + self.nl) #DEBUG

            # validate answer
            if len(answer) != 1:
                self.myerr.write('invalid menu entry' + self.nl)
                self.myerr.write(self.nl)
                continue

            # look for answer
            found = False
            for x in self.entries:
                if x['key'] == answer:
                    found = True
                    if type(x['sub']) in [type(None)]:
                        return x['key']

                    elif type(x['sub']) in [type(menu_system())]:
                        #sub menu system
                        self.myout.write(self.nl)
                        recurse = x['sub'].run()
                        if not(type(recurse) in [type('a')]): recurse = '0'
                        return x['key'] + recurse

                    elif type(x['sub']) in [type(lambda: True)]:
                        # lambda functions that run each time
                        # if they return true, you exit menu
                        # if they return false, stay in menu
                        if x['sub']():
                            return x['key']
                        else: continue

            if not(found):
                self.myerr.write('invalid menu entry' + self.nl)
                self.myerr.write(self.nl)
                continue

            answer = None

