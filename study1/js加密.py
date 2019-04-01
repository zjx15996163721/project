import execjs
ctx = execjs.compile("""
function add(x, y){
    return x+y;
}
""")
print(ctx.call("add", 1, 2))


