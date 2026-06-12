// ====================== 5 循环语句(5.0/5.1 强制规则，其余拓展) ======================

// 【语义错误】for迭代区间表达式非整型
fn program_5_2__2(mut n:i32) 
{
    for mut i in 1..n+0.1 {
        n=n-1;
    }
}

// 【语义错误】break 不在循环体内
fn program_5_4__2() {
    break;
}

// 【语义错误】continue 不在循环体内
fn program_5_4__4() {
    continue;
}