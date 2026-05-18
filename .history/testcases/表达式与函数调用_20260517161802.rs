fn test_expressions(mut a:i32, mut b:i32) {
    // 括号与基本算术表达式 [cite: 124, 151, 152, 155, 156]
    ((a));
    1+2;
    3-4;
    1*2;
    3/4;
    
    // 组合运算：乘除优先级高于加减应在语法树体现
    a + b * 2;
    
    // 比较运算 [cite: 147, 148]
    1<2;
    3>4;
    a == b;
    a != 0;
}

fn program_3_5__2() {
    // 函数调用 [cite: 161]
    program_1_5(); 
    test_expressions(1, 2); 
}