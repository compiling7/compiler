// ====================== 6 引用、借用(拓展，非强制规则) ======================

// 6.1 不可变变量(无mut)
fn program_6_1__1() {
    let a:i32=1;
    let b=2;
}

// 6.2 不可变引用 &T（&类型不在语法检查范围内，以实际i32变量代替引用测试）
fn program_6_2__1() {
    let a:i32=1;
    let b:i32=a;
}

// 合法：多个不可变引用共存（以普通变量测试）
fn program_6_2__2() {
    let mut a:i32=1;
    let b:i32=a;
    let c:i32=a;
}

// 6.3 可变引用 &mut T（&mut类型不在语法检查范围内，以实际mut变量代替）
fn program_6_3() {
    let mut a:i32=1;
    let mut b:i32=a;
}

// 6.4 解引用 *（解引用不在语法检查范围内，以直接赋值测试）
fn program_6_4__1() {
    let mut a:i32=1;
    let mut b:i32=a;
    b=2;
}
