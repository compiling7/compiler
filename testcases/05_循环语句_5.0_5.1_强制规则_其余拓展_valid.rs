// ====================== 5 循环语句(5.0/5.1 强制规则，其余拓展) ======================

// 5.0 循环总规则、5.1 while 条件循环
fn program_5_1(mut n:i32) { 
    while n>0 { 
        n=n-1;
    }
}

// 5.2 for循环(拓展)
fn program_5_2__1(mut n:i32) 
{
    for mut i in 1..n+1 {
        n=n-1;
    }
}

// 5.3 loop无限循环(拓展)
fn program_5_3() {
    loop {
    } 
}

// 5.4 break / continue 跳转(拓展)
fn program_5_4__1() { 
    while 1==1 {
        break;
    } 
}

fn program_5_4__3() { 
    while 1==0 {
        continue;
    } 
}