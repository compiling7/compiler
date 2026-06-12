// ====================== 7 函数表达式块、选择/循环表达式(拓展) ======================

// 7.1 函数表达式块（不支持表达式块语法，改为独立赋值语句）
fn program_7_1(mut x:i32,mut y:i32) {
    let mut t:i32=x*x+x;
    t=t+x*y;
    let mut z:i32=t;
}

// 7.2 表达式块作为函数体
fn program_7_2(mut x:i32,mut y:i32) -> i32 {
    let mut t:i32=x*x+x;
    t=t+x*y;
    return t;
}

// 7.3 选择表达式 if-else 作为表达式（不支持，改为普通if-else赋值）
fn program_7_3(mut a:i32)
{
    let mut b:i32;
    if a>0 {
        b=1;
    } else {
        b=0;
    }
}

// 7.4 loop表达式 + break 带返回值（不支持break带值，改为普通loop+break）
fn program_7_4__1() {
    let mut a:i32=0;
    loop {
        a=1;
        break;
    }
}
