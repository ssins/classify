from App.Temp import temp
@temp.route('/')
def root():
   return 'temp'
