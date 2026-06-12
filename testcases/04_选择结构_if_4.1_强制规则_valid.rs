// ====================== 4 选择结构 if(4.1 强制规则) ======================

// 4.1 基础if语句(无else)
fn program_4_1(mut a:i32) -> i32 {
    if a>0 { 
        return 0; 
    }
    return 1;
}

// 4.2 if-else(拓展)
fn program_4_2(mut a:i32) -> i32 {
    if a>0 { 
        return 0; 
    } else { 
        return 1;
    }
}

// 4.3 if-else if-else 多分支(拓展)
fn program_4_3(mut a:i32) -> i32 {
    if a>0 { 
        return a+1;
    } else if a<0 {
        return a-1;
    } else { 
        return 0;
    }
}