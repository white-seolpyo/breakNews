from traceback import format_exc


from news import main
from message import err


try: main()
except:
    e = format_exc()
    err(e)

