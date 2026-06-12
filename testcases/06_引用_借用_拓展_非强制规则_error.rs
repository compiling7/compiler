// ====================== 6 引用、借用(拓展，非强制规则) ======================

// 【语义错误】不可变变量禁止二次赋值
fn program_6_1__2() { 
    let c:i32=1;
    c=2;
}

// 【语义错误】可变引用与其他引用共存
fn program_6_3__4() { 
    let mut a:i32=1; 
    let b=&a; 
    let mut c=&mut a;
}

// 【语义错误】不可变变量不能创建可变引用
fn program_6_3__5() {
    let a:i32=1;
    let mut b=&mut a;
}

// 【语义错误】对非引用类型解引用
fn program_6_4__2() { 
    let mut a:i32=1;
    let mut b=*a;
}

// 【语义错误】不可变引用禁止修改数据
fn program_6_4__3() { 
    let mut a:i32=1; 
    let mut b=&a;
    *b=2;
}