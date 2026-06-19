int32_t sub_203()
{
    int32_t entry_ebx;
    /* jump -> *(entry_ebx + 0x80be00) */
}

int32_t sub_5d7(void* arg1 @ esi)
{
    int32_t var_4 = *(arg1 - 0xc);
    /* undefined */
}

int32_t __convention("fastcall") sub_5e6(int32_t arg1)
{
    /* jump -> arg1 */
}

int32_t __convention("regparm") sub_8b5(void* arg1, int16_t arg2, int32_t* arg3 @ ebp, uint16_t* arg4 @ esi, int32_t arg5 @ edi, long double arg6 @ st0)
{
    *(arg1 + 0x6f727245) += arg2;
    int32_t ecx;
    int16_t es;
    ecx = __les_gprz_memp(*(arg5 * 3 - 0x40));
    int32_t eflags;
    __outsd(arg2, *arg4, arg4, eflags);
    uint32_t edi = arg3[1];
    int32_t esi_1 = arg3[2];
    arg3[5];
    arg3[6];
    int32_t fsbase;
    *(fsbase + esi_1 - 8);
    arg3[8] = arg3[8];
    __ud0_gpr32_gpr32(edi, edi);
    /* jump -> *(esi_1 + 0x42db870a) */
}

int32_t sub_964()
{
    bool o;
    
    if (o)
        /* undefined */
    
    /* jump -> 0x968 */
}

int32_t __convention("regparm") sub_983(int32_t arg1)
{
    int32_t eflags;
    int32_t eflags_1;
    char temp0;
    char temp1;
    temp0 = __aas(arg1, *(&arg1 + 1), eflags);
    arg1 = temp0;
    *(&arg1 + 1) = temp1;
    int32_t var_4 = arg1;
    int32_t var_8 = 0xab018072;
    /* undefined */
}

int32_t __convention("regparm") sub_995(int32_t arg1, int32_t arg2, int32_t arg3, uint16_t* arg4 @ esi)
{
    int32_t eflags;
    __out_dx_al(arg2, arg1, eflags);
    __outsd((arg2 - 1), *arg4, arg4, eflags);
    int32_t var_4 = 0xf0fec078;
    int64_t msrs = __wrmsr(arg1 + 1, arg2 - 1, arg3);
    int32_t var_8 = arg2 - 1;
    __int1();
    /* undefined */
}

int32_t sub_a25()
{
    int32_t eax;
    *(&eax + 1) = 0xfa;
    /* undefined */
}

int32_t __convention("regparm") sub_a3a(int32_t arg1, void* arg2, int32_t arg3, int32_t arg4 @ esi, int32_t arg5 @ edi)
{
    arg1 = arg1 * *(arg4 + (arg2 << 3) - 0xe55090e);
    
    if (arg3)
        trap(0xd);
    
    arg1 = arg1 * *(arg2 - 0xb051c0f);
    int32_t eflags;
    arg1 = __salc(eflags);
    int32_t entry_ebx;
    char temp1 = arg1 % *(&entry_ebx + 1);
    arg1 = arg1 / *(&entry_ebx + 1);
    *(&arg1 + 1) = temp1;
    *arg4 - *arg5;
    arg1 = __salc(eflags);
    arg1 = arg1 * *(arg2 + ((arg5 + 1) << 3) - 0x6295d0b);
    /* jump -> *(arg1 + 0xc7d18afa) */
}

int32_t __convention("regparm") sub_a85(void* arg1, int32_t arg2, int32_t arg3, void* arg4 @ esi, int32_t arg5 @ edi)
{
    *(arg5 * 2);
    *(arg1 + (arg2 << 2) + 0x398e0ef6);
    *(arg1 + (arg2 << 2) + 0x398e0ef6) = arg3;
    char temp2 = arg1;
    char temp3 = *(&arg1 + 1);
    arg1 = arg1 * *(&arg1 + 1);
    *(&arg2 + 1) = *(&arg2 + 1) + *(&arg2 + 1);
    int16_t ss;
    *(arg4 + 0x12d6ffff) = ss;
    *(arg2 - 0x7729eb0a);
    uint32_t var_4 = ss;
    *(arg4 + 0x18d638fc);
    int16_t var_8 = arg4;
    arg2 = arg2 - *(&arg2 + 1);
    *(&arg2 + 1) ^= 0xfc;
    int32_t temp0_1 = *(arg1 - 0x73a1e10a);
    *(arg1 - 0x73a1e10a) = arg1;
    int32_t eax;
    int16_t entry_ebx;
    eax = temp0_1 / *(&entry_ebx + 1);
    *(&eax + 1) = temp0_1 % *(&entry_ebx + 1);
    /* jump -> eax */
}

int32_t sub_abd()
{
    int16_t es;
    uint32_t var_4 = es;
    /* undefined */
}

int32_t __convention("fastcall") sub_ad9(int32_t arg1, int16_t arg2, void* arg3 @ esi, int32_t arg4 @ edi)
{
    int32_t esp_1 = &__return_addr ^ arg4;
    
    if (esp_1 && arg1 == 1)
        trap(0xd);
    
    *(arg3 - 0xf000968) = -(*(arg3 - 0xf000968));
    *(&arg2 + 1) *= 2;
    int32_t eax;
    int32_t entry_ebx;
    eax = *(entry_ebx + 0x4f61983());
    int16_t es;
    *(esp_1 - 4) = es;
    *(arg3 + 0x70391fff) = ~*(arg3 + 0x70391fff);
    *arg3 - *arg4;
    /* undefined */
}

int32_t __convention("regparm") sub_c05(void* arg1, int32_t arg2, int32_t arg3, void* arg4 @ esi, int32_t arg5 @ edi, int32_t arg6, int32_t arg7, int16_t arg8, int32_t arg9, int32_t arg10)
{
    int32_t var_4 = *(arg4 - 0x3ce4704);
    bool z;
    bool s;
    bool o;
    
    if (z || s != o)
    {
        if (z || s != o)
            /* jump -> 0xbff */
        
        /* tailcall */
        return sub_c14(arg1);
    }
    
    int32_t eflags;
    arg1 = __salc(eflags);
    char entry_ebx;
    arg1 = entry_ebx;
    *(arg2 + (arg1 << 2) + 0xc8cf852) += arg3;
    bool c = arg3 + *(arg4 + (arg5 << 3)) < arg3;
    *(arg1 + 0x1914edf0) = arg1;
    
    do
        eflags = __sti(eflags);
     while (c);
    
    __in_oeax_dx(arg8, eflags);
    /* undefined */
}

int32_t __convention("regparm") sub_c14(int32_t arg1)
{
    /* undefined */
}

int32_t sub_c16()
{
    /* undefined */
}

int32_t __convention("regparm") sub_c20(int32_t* arg1, int32_t arg2)
{
    bool c;
    *arg1 = *arg1 + arg2;
    int32_t eflags;
    __sti(eflags);
    /* undefined */
}

void* __convention("regparm") sub_c26(char* arg1, char* arg2, int32_t arg3, int32_t* arg4 @ esi, int32_t* arg5 @ edi, int64_t arg6 @ st4, int32_t arg7[0x2] @ st7)
{
    int32_t eflags;
    int32_t eflags_2;
    char temp0_4;
    char temp1_1;
    temp0_4 = __aas(arg1, *(&arg1 + 1), eflags);
    arg1 = temp0_4;
    *(&arg1 + 1) = temp1_1;
    int32_t entry_ebx;
    void* ebx = entry_ebx - arg5;
    int32_t* var_4 = arg4;
    char* var_8 = arg1;
    int32_t var_c = arg3;
    char* var_10 = arg2;
    void* var_14 = ebx;
    int32_t* var_18 = &var_14;
    int32_t ebp;
    int32_t var_1c = ebp;
    int32_t* var_20 = arg4;
    int32_t* var_24 = arg5;
    *(&arg2 + 1) ^= *arg2;
    arg1 = *0x2056d656;
    char temp1 = arg1;
    char temp2 = *arg1;
    arg1 += *arg1;
    bool c = temp1 + temp2 < temp1;
    char* var_28 = arg1;
    int32_t var_2c = arg3;
    char* var_30 = arg2;
    void* var_34 = ebx;
    int32_t* var_38 = &var_34;
    int32_t var_3c = ebp;
    int32_t* var_40 = arg4;
    int32_t* var_44 = arg5;
    __int1();
    int32_t* esp = &var_40;
    int32_t eflags_1 = __sti(eflags_2);
    int32_t* eax;
    eax = __salc(eflags_1);
    int32_t temp3_1;
    int32_t temp4_1;
    
    do
    {
        arg4[-0x1dfea6a] = arg4[-0x1dfea6a] - arg3;
        eax = __salc(eflags_1);
        int16_t es;
        *(esp - 4) = es;
        esp -= 3;
        temp3_1 = *arg4;
        temp4_1 = *arg5;
        c = temp3_1 < temp4_1;
        arg4 = &arg4[1];
        arg5 = &arg5[1];
        arg3 -= 1;
    } while (temp3_1 == temp4_1 || arg3);
    *(esp - 4) = arg4;
    void* result;
    result = (eax + 1) - 0x19;
    *arg5 = *arg4;
    char* esi = arg4 + 1;
    /* unimplemented  {enter 0xa0fb, 0xd6} */
    __int1();
    result ^= 0xc8;
    *(&arg2 + 1) = *(&arg2 + 1) + 0x58;
    *(result - 0x2c77f25) |= arg3;
    _m_psrad(arg7, arg6);
    *esi s>>= 0xc0;
    result = __salc(eflags_1);
    return result;
}

int32_t __convention("regparm") sub_c6a(int16_t arg1)
{
    int32_t eflags;
    int32_t eflags_1;
    char temp0;
    char temp1;
    temp0 = __aas(arg1, *(&arg1 + 1), eflags);
    arg1 = temp0;
    *(&arg1 + 1) = temp1;
    /* undefined */
}

int32_t __convention("fastcall") sub_c87(int32_t arg1) __pure
{
    return arg1;
}

int32_t __convention("regparm") sub_c97(int16_t arg1, int32_t, char* arg3, long double arg4 @ st0, long double arg5 @ st4)
{
    char temp0_2 = *arg3;
    *arg3 += 1;
    int32_t eflags;
    int32_t eflags_1;
    char temp0;
    char temp1;
    temp0 = __aas(arg1, *(&arg1 + 1), eflags);
    arg1 = temp0;
    *(&arg1 + 1) = temp1;
    arg1 = __salc(eflags_1);
    
    do
    {
        /* unimplemented  {fdivp st4, st0} */
        /* unimplemented  {fdivp st4, st0} */
        int16_t top = top + 1;
        arg3 -= 1;
    } while (temp0_2 != 0xff && arg3);
    
    if (arg3 == 1)
        /* tailcall */
        return sub_ca3();
    
    void* entry_ebx;
    int16_t cs;
    *(entry_ebx - 0x10381c1) = cs;
    *(arg3 - 1) += (arg3 - 1);
    /* undefined */
}

int32_t sub_ca3()
{
    int32_t eflags;
    int32_t eax;
    eax = __salc(eflags);
    eax = __in_al_immb(0xff, eflags);
    bool o;
    
    if (!o)
        /* undefined */
    
    /* tailcall */
    return sub_caa();
}

int32_t sub_caa()
{
    int32_t eflags;
    int32_t eax;
    eax = __salc(eflags);
    /* undefined */
}

int32_t __convention("regparm") sub_cf6(char arg1)
{
    int16_t __return_addr_1;
    __return_addr = __return_addr_1;
    /* undefined */
}

int32_t __convention("regparm") sub_cfa(int32_t* arg1, int32_t arg2, int32_t arg3, int32_t arg4 @ ebp, int32_t arg5 @ esi, void* arg6 @ edi, long double arg7 @ st0, long double arg8 @ st1, int80_t arg9 @ st7)
{
    int32_t temp2 = *arg1 >> 1;
    *arg1 = temp2;
    int32_t temp0 = COMBINE(arg2, arg1) / arg1;
    char* ecx = arg3 - 1;
    int32_t eflags_1;
    int32_t eax;
    char* entry_ebx;
    void* esp;
    int32_t eflags;
    
    if (!temp2 || ecx)
    {
        char temp0_1 = *ecx;
        *ecx = temp0;
        eax = temp0_1;
        eax += 1;
        eax ^= 0xc8;
        /* unimplemented  {enter 0x86fb, 0x7f} */
        *(eax + 0x72d6f022) += 1;
        
        if (ecx)
        {
            char* var_8 = ecx;
            ecx = 0x78;
            int32_t result;
            int32_t ecx_1;
            int16_t* edx_2;
            int16_t cs;
            result = 0x2ea0760(var_8, cs);
            void arg_20;
            void* esp_2 = &arg_20 + arg4 + 1;
            ecx_1 = *(arg6 * 3 - 0x1af5fe08);
            *(esp_2 + ecx_1 + 0x28fe01bb) += ecx_1;
            result = *entry_ebx;
            int16_t es;
            *edx_2 = es;
            int32_t eflags_2;
            int32_t eip_2;
            eip_2 = __into(eflags);
            *(esp_2 - 4) = result;
            *(esp_2 - 8) = ecx_1;
            *(esp_2 - 0xc) = edx_2;
            *(esp_2 - 0x10) = 0xdd60e300;
            *(esp_2 - 0x14) = esp_2 - 0x10;
            *(esp_2 - 0x18) = arg4 + 1;
            *(esp_2 - 0x1c) = arg5 * 2;
            *(esp_2 - 0x20) = arg6;
            result = __in_al_immb(0xd6, eflags_2);
            return result;
        }
        
        eflags_1 = __sti(eflags);
    }
    else
    {
        __out_immb_oeax(0x85, temp0, eflags);
        int32_t edx_1;
        eax = 0xf3fa5530();
        
        while (true)
        {
            bool cond:1_1 = *(eax + (edx_1 << 1) - 0x18) <= *(&entry_ebx + 1);
            eflags_1 = __cli(eflags);
            
            if (!cond:1_1)
                break;
            
            eflags = __cli(eflags_1);
        }
        
        __int1();
        *0xfa7ff8c5 = eax;
        *(__return_addr - 4) = edx_1;
        esp = __return_addr - 4;
        *0x7454f13e;
        *0x7454f13e = ROLD(*0x7454f13e, 1);
        bool c_1 = /* bool c_1 = unimplemented  {rol dword [0x7454f13e], 0x1} */;
        arg7 - arg9;
        long double st1_1;
        bool c1_1;
        st1_1 = __fyl2x(arg7, arg8);
        *ecx = *ecx - 5;
    }
    void** edi_1 = arg6 + 1;
    eax = eax - 4;
    int16_t ss;
    *(esp - 4) = ss;
    *(esp - 8) = ss;
    *(edi_1 + 0x5f1ebb15);
    *(edi_1 + 0x5f1ebb15) = 0x1cfc1afe;
    bool c_4 = /* bool c_4 = unimplemented  {rcr ebx, 0xe9} */;
    /* unimplemented  {fucomp st0, st1} f- unimplemented  {fucomp st0, st1} */
        - /* unimplemented  {fucomp st0, st1} f- unimplemented  {fucomp st0, st1} */;
    /* unimplemented  {fucomp st0, st1} */
    char temp6 = eax;
    eax = temp6 - 0x3b;
    bool z = !(temp6 - 0x3b);
    bool i = /* bool i = unimplemented  {adc al, 0xc5} */;
    
    if (z || ecx == 1)
        trap(0xd);
    
    int32_t eflags_3;
    char temp0_4;
    char temp1_1;
    temp0_4 = __aas(eax, *(&eax + 1), eflags_1);
    eax = temp0_4;
    *(&eax + 1) = temp1_1;
    
    while (z || temp6 - 0x3b < 0 != i)
        edi_1 = *edi_1;
    
    /* undefined */
}

int32_t __convention("regparm") sub_d2c(int32_t arg1, char* arg2, int32_t arg3, int32_t arg4 @ ebp, void* arg5 @ esi, int32_t arg6 @ edi)
{
    int32_t edi_1 = arg6 & arg3;
    *(&arg2 + 1) = 0xb2;
    int32_t eflags;
    int32_t eflags_1 = __sti(eflags);
    int32_t i;
    i = __salc(eflags_1);
    int32_t* entry_ebx;
    *(entry_ebx + i) += i;
    int32_t eax;
    
    while (true)
    {
        eflags_1 = __sti(eflags_1);
        *(arg5 + 0x34010401);
        /* unimplemented  {enter 0xfbc8, 0x86} */
        
        while (i > -(*(arg5 + 0x34010401)))
            /* nop */
        
        char temp3_1 = *arg2 & 0xf0;
        *arg2 = temp3_1;
        eax = __salc(eflags_1);
        
        if (temp3_1 >= 0)
            break;
        
        *0xcf96050 = 0xcf96054;
        *0xcf9604c = eax;
        *0xcf96048 = arg3;
        *0xcf96044 = arg2;
        *0xcf96040 = entry_ebx;
        *0xcf9603c = 0xcf96040;
        *0xcf96038 = arg4;
        *0xcf96034 = arg5;
        *0xcf96030 = edi_1;
        eax |= 0x21;
        i = 0x3040f12();
    }
    
    eax = __salc(eflags_1);
    int16_t cs;
    *0xcf96050 = cs;
    *0xcf9604c = arg3;
    arg3 = 0x78;
    int32_t result;
    int32_t ecx;
    int16_t* edx;
    result = 0x2ea0760();
    ecx = *(edi_1 * 3 - 0x1af5fe08);
    *(arg4 + 0xcf9604d + ecx + 0x28fe01bb) += ecx;
    result = *entry_ebx;
    int16_t es;
    *edx = es;
    int32_t eflags_2;
    int32_t eip;
    eip = __into(eflags_1);
    *(arg4 + 0xcf96049) = result;
    *(arg4 + 0xcf96045) = ecx;
    *(arg4 + 0xcf96041) = edx;
    *(arg4 + 0xcf9603d) = 0xdd60e300;
    *(arg4 + 0xcf96039) = arg4 + 0xcf9603d;
    *(arg4 + 0xcf96035) = arg4 + 1;
    *(arg4 + 0xcf96031) = arg5 * 2;
    *(arg4 + 0xcf9602d) = edi_1;
    result = __in_al_immb(0xd6, eflags_2);
    return result;
}

int32_t __convention("regparm") sub_d80(char arg1)
{
    int32_t eflags;
    int32_t eflags_1;
    char temp0;
    temp0 = __das(arg1, eflags);
    /* undefined */
}

int32_t __convention("regparm") sub_db2(int32_t arg1, int16_t* arg2, void* arg3, int32_t arg4 @ edi)
{
    int32_t entry_ebx;
    int16_t var_4 = entry_ebx;
    *(&arg3 + 1) |= entry_ebx;
    entry_ebx u>>= 0xa3;
    bool c = /* bool c = unimplemented  {shr bl, 0xa3} */;
    arg1 = arg1 + 5;
    int32_t eflags;
    arg1 = __in_al_dx(arg2, eflags);
    *(arg3 - 0x29aeba0f) -= 2;
    int16_t cs;
    uint32_t var_6 = cs;
    int32_t eflags_2 = __sti(eflags);
    arg1 = __salc(eflags_2);
    __int1();
    arg1 ^= 0x8a;
    
    if (arg3)
    {
        arg1 = __in_al_dx(arg2, __sti(eflags_2));
        arg1 = *0xec28a2f1;
        /* undefined */
    }
    
    int32_t edi = arg4 + *(entry_ebx - 0x229f1d00);
    *arg2 = var_4;
    int32_t eflags_1;
    int32_t eip;
    eip = __into(eflags_2);
    int32_t var_a = arg1;
    void* var_e = arg3;
    int16_t* var_12 = arg2;
    int32_t var_16 = entry_ebx;
    int32_t* var_1a = &var_16;
    int32_t ebp;
    int32_t var_1e = ebp;
    int32_t esi;
    int32_t var_22 = esi;
    int32_t var_26 = edi;
    arg1 = __in_al_immb(0xd6, eflags_1);
    return arg1;
}

int32_t sub_ddd()
{
    bool z;
    bool s;
    bool o;
    
    if (!z && s == o)
        /* undefined */
    
    /* jump -> 0xde0 */
}

int32_t __convention("regparm") sub_de2(int32_t arg1, char* arg2)
{
    int16_t entry_ebx;
    *arg2 += *(&entry_ebx + 1);
    arg1 = *0x36caf128;
    /* undefined */
}

int32_t __convention("regparm") sub_ded(int32_t arg1, int32_t* arg2, int32_t arg3, void* arg4 @ ebp, int32_t arg5 @ edi, long double arg6 @ st0)
{
    bool c_1 = /* bool c_1 = unimplemented  {sbb eax, 0x21f710ca} */;
    arg2 = arg2 - *0xeb1fc11c;
    char* esi;
    int16_t es;
    esi = __les_gprz_memp(*(arg4 + 0x4528fcdb));
    int32_t eflags;
    int32_t eax;
    eax = __salc(eflags);
    
    if (arg5 == 0xfffffffe || arg3 == 1)
    {
        eax = __in_al_immb(0xf6, eflags);
        eax ^= 0xd6;
        *0x3a4ff0f9 = eax;
        trap(0xd);
    }
    
    if (arg3 == 2)
    {
        *arg2 = arg6;
        int32_t eax_1;
        eax_1 = __salc(__sti(eflags));
        /* undefined */
    }
    
    eax = __salc(eflags);
    int32_t ecx_1;
    ecx_1 = (arg3 - 2) + *esi;
    eax = __salc(__sti(eflags));
    __int1();
    eax ^= 0x8a;
    
    if (!ecx_1)
        /* jump -> sub_db2-0x42 */
    
    /* jump -> sub_db2-8 */
}

int32_t __convention("regparm") sub_f4d(int32_t arg1, int16_t* arg2, int32_t arg3, int32_t arg4 @ ebp, int32_t arg5 @ esi, void* arg6 @ edi)
{
    void* var_4 = arg6;
    int32_t* esp = &var_4;
    int32_t eflags;
    int32_t eflags_1 = __sti(eflags);
    void* entry_ebx;
    char temp0 = *(&entry_ebx + 1);
    char temp1 = *(entry_ebx - 0x44aa6e6f);
    bool c;
    *(&entry_ebx + 1) = temp0 + temp1;
    bool c_1 = temp0 + temp1 < temp0 || (c && temp0 + temp1 == temp0);
    *0x55c3ffff += 1;
    
    while (true)
    {
        char temp2_1 = arg1;
        arg1 = temp2_1 - 0x40;
        arg2 = arg2 + *(entry_ebx + (arg1 << 3));
        *(&entry_ebx + 1) u>>= 0xba;
        int16_t es;
        *arg2 = es;
        __int1();
        arg1 = __salc(eflags_1);
        int32_t eax;
        eax = __les_gprz_memp(*(arg6 - 0x3b3b6bbd));
        *(eax + (entry_ebx << 3) - 0x3c);
        eflags_1 = __sti(eflags_1);
        int32_t eax_2;
        eax_2 = __salc(eflags_1);
        arg1 = __in_oeax_dx(arg2, eflags_1);
        *arg5;
        int32_t temp3_1 = arg5;
        arg5 &= arg4;
        c_1 = false;
        
        if (!arg3)
            break;
        
        while (temp3_1 & arg4)
            /* nop */
        
        *(esp - 3) = arg4;
        esp -= 3;
    }
    
    return arg1;
}

void sub_f86() __noreturn
{
    int16_t ecx;
    int16_t entry_ebx;
    *(&ecx + 1) = *(&__return_addr + 1) & *(&entry_ebx + 1);
    
    while (true)
        /* nop */
}

void __convention("regparm") sub_f8e(int16_t arg1, int32_t, int16_t arg3) __noreturn
{
    char temp1 = arg1 % *(&arg3 + 1);
    arg1 = arg1 / *(&arg3 + 1);
    *(&arg1 + 1) = temp1;
    int32_t eflags;
    __sti(eflags);
    
    while (true)
        /* nop */
}

int32_t sub_f94() __pure
{
    int32_t result;
    *(&result + 1) = 0xf6;
    return result;
}

int32_t __convention("regparm") sub_fbf(void* arg1, int32_t arg2, int32_t arg3, void* arg4 @ esi, void* arg5 @ edi)
{
    int32_t eflags;
    __out_dx_al(arg2, arg1, eflags);
    arg1 = __salc(eflags);
    char* entry_ebx;
    *(&arg1 + 1) &= *entry_ebx;
    arg1 = __salc(eflags);
    __int1();
    arg1 = __salc(eflags);
    *(arg1 + 0x2f15c02);
    arg1 -= 0xf;
    
    while (true)
    {
        int32_t eax_2;
        eax_2 = entry_ebx[__in_oeax_dx(arg2, eflags)];
        int16_t* esp;
        *esp;
        esp = &esp[1];
        __int1();
    }
}

long double __convention("regparm") sub_16a2(int32_t arg1, int32_t arg2, int32_t* arg3)
{
    int32_t var_4 = arg1;
    int32_t* var_8 = arg3;
    int32_t var_c = arg2;
    int32_t ebx;
    int32_t var_10 = ebx;
    int32_t* var_14 = &var_10;
    int32_t ebp;
    int32_t var_18 = ebp;
    int32_t esi;
    int32_t var_1c = esi;
    int32_t edi;
    int32_t var_20 = edi;
    *(&arg3 + 1) = *(&arg3 + 1) - *(arg3 - 0x17af1eb5);
    /* unimplemented  {sbb ch, byte [ecx-0x17af1eb5]} */
    char temp1 = arg1 % *(&arg1 + 1);
    arg1 = arg1 / *(&arg1 + 1);
    *(&arg1 + 1) = temp1;
    int32_t* var_24 = arg3;
    return *arg3;
}

int32_t sub_16bb() __pure
{
    return;
}

int32_t sub_1733(int32_t arg1 @ esi, void* arg2 @ edi)
{
    int16_t eax;
    int32_t ecx;
    int16_t edx;
    eax = (*arg1)();
    *(arg2 + 0x3fef61c);
    *(arg2 + 0x3fef61c) &= eax;
    int32_t eflags;
    __cli(eflags);
    int32_t entry_ebx;
    *(entry_ebx + (arg1 << 1) - 0x78400934) = *(entry_ebx + (arg1 << 1) - 0x78400934) - *(&eax + 1);
    bool c = /* bool c = unimplemented  {sbb byte [ebx+esi*2-0x78400934], ah} */;
    *(&edx + 1) = *(&edx + 1) - *(&edx + 1);
    /* jump -> ecx */
}

int80_t __convention("regparm") sub_1848(int32_t arg1, int32_t arg2, int32_t arg3, void* arg4 @ esi, int32_t arg5 @ edi, long double arg6 @ st0, long double arg7 @ st3)
{
    *(arg2 - 6);
    int32_t edi = arg5 + *(arg2 - 1);
    int32_t eflags;
    __out_dx_oeax(arg2, arg1, eflags);
    uint8_t* edi_1;
    uint8_t temp0;
    temp0 = __insb(edi, arg2, eflags);
    *edi_1 = temp0;
    int32_t eflags_1;
    int32_t eip;
    eip = __into(eflags);
    int32_t eflags_2 = __cli(eflags_1);
    int32_t eax_2;
    int32_t ecx_1;
    int32_t edx;
    eax_2 = 0xfa9d0c14();
    void arg_4;
    bool c = edi_1 < &arg_4;
    bool p = /* bool p = unimplemented  {cmp edi, esp} */;
    bool a = /* bool a = unimplemented  {cmp edi, esp} */;
    int32_t eflags_3 = __cli(eflags_2);
    eax_2 = *0xfaa45bfa;
    bool d;
    __return_addr = (edi_1 + -(&arg_4) ? 1 : 0) << 0xb | (d ? 1 : 0) << 0xa
        | (edi_1 - &arg_4 < 0 ? 1 : 0) << 7 | (edi_1 == &arg_4 ? 1 : 0) << 6 | (a ? 1 : 0) << 4
        | (p ? 1 : 0) << 2 | (c ? 1 : 0);
    
    if (c)
        /* tailcall */
        return sub_1873(ecx_1);
    
    *(arg4 - 0x2a) = *(arg4 - 0x2a) + 0x50000c6;
    char temp1 = eax_2 % *(arg4 + (edx << 3));
    eax_2 = eax_2 / *(arg4 + (edx << 3));
    *(&eax_2 + 1) = temp1;
    *__return_addr;
    int32_t* entry_ebx;
    *entry_ebx = 0x58fa3ef6;
    eax_2 = __salc(eflags_3);
    __cli(eflags_3);
    *__return_addr = arg4;
    /* undefined */
}

int32_t __convention("fastcall") sub_1873(int32_t arg1)
{
    int32_t eflags;
    __cli(eflags);
    /* jump -> *(arg1 + 0xffffffff) */
}

int32_t __convention("regparm") sub_1878(int32_t arg1, int32_t arg2, char* arg3 @ esi, char* arg4 @ edi)
{
    *arg4 = arg1;
    void* edi = &arg4[1];
    int32_t eflags;
    int32_t eflags_1 = __cli(eflags);
    arg1 = *arg3;
    int32_t eflags_2;
    int32_t eip;
    eip = __into(eflags_1);
    *edi;
    int32_t* edi_1 = edi + 1;
    int32_t ecx;
    *(&ecx + 1) = 0xb2;
    __out_immb_oeax(0xf8, arg1, eflags_2);
    *edi_1 -= 1;
    /* jump -> arg2 */
}

void __convention("regparm") sub_19d0(uint32_t arg1, int32_t arg2, char* arg3, void* arg4 @ ebp, uint32_t arg5 @ edi) __noreturn
{
    int16_t ss;
    uint32_t var_8 = ss;
    *(arg4 + 0x53);
    *(arg4 + 0x53) |= arg3;
    *arg3 = *arg3 - arg3;
    *0x1c94091a;
    *arg3;
    __ud0_gpr32_gpr32(arg5, arg1);
    trap(0xd);
}

long double __convention("fastcall") sub_2018(float* arg1, int32_t arg2, void* arg3 @ ebp, int32_t arg4 @ edi, long double arg5 @ st0, long double arg6 @ st5)
{
    void* var_4 = arg3;
    int32_t eflags;
    void* eax;
    eax = __in_al_dx(arg2, eflags);
    __out_immb_oeax(0xfd, eax, eflags);
    arg1 |= *(arg3 - 0xe3cd504);
    void* entry_ebx;
    int32_t* edx = arg2 - *(entry_ebx - 0xc);
    int32_t* edi = -(arg4);
    *edi -= 1;
    entry_ebx u>>= 1;
    long double x87_r0 = arg5 * *(eax - 0x7dea3684);
    *edx -= 1;
    edx |= *(arg1 - 0x2001f1);
    int32_t temp0_1 = COMBINE(edx, eax) / *edi;
    int16_t temp1 = COMBINE(edx, eax) % *edi;
    int32_t* var_8 = edi;
    __int1();
    long double result = *arg1 - x87_r0;
    __out_dx_oeax(temp1 + 1, temp0_1, eflags);
    
    while (true)
    {
        arg1 -= 1;
        
        if (!arg1)
            break;
        
        edi -= arg3;
    }
    
    __out_dx_oeax(temp1 + 1, temp0_1, eflags);
    int32_t eflags_1;
    char temp0_2;
    char temp1_1;
    temp0_2 = __aaa(temp0_1, *(&temp0_1 + 1), eflags);
    int32_t eax_1;
    eax_1 = temp0_2;
    *(&eax_1 + 1) = temp1_1;
    return result;
}

int32_t sub_20b1()
{
    int32_t eax;
    eax = *0xfe1542f0;
    /* undefined */
}

int32_t sub_213d()
{
    *0x77f1580f;
    /* undefined */
}

void __convention("regparm") sub_2216(int32_t arg1, int16_t arg2, void* arg3 @ esi, void* arg4 @ edi, long double arg5 @ st0) __noreturn
{
    int32_t var_4 = *(arg4 + 0xf200ac);
    *arg3 - *arg4;
    uint16_t* esi = arg3 + 4;
    *(arg4 - 0x22);
    int32_t entry_ebx;
    arg1 = *(entry_ebx + arg1);
    int32_t eflags;
    __outsd(arg2, *esi, esi, eflags);
    trap(0xd);
}

int32_t __convention("regparm") sub_25d3(int32_t, char* arg2)
{
    bool c;
    *arg2 = *arg2 - 0x21;
    /* undefined */
}

int32_t sub_260f(int32_t arg1 @ ebp, uint16_t* arg2 @ esi)
{
    char eax;
    void* ecx;
    int16_t edx;
    int32_t edi;
    eax = (*(edi + 0x7c7de5f3))();
    int32_t eflags;
    __outsb(edx, *arg2, arg2, eflags);
    __sti(eflags);
    *(ecx - 0x157010f) ^= &__return_addr;
    /* jump -> *(arg1 + 0xa34c4378) */
}

int32_t __convention("fastcall") sub_2651(int32_t arg1)
{
    __int1();
    bool z;
    
    if (z || arg1 != 1)
        /* undefined */
    
    int32_t eax;
    int32_t edx;
    void* edi;
    int16_t cs;
    /* tailcall */
    return sub_2657(eax, edx, edi, arg1 - 1, cs);
}

int32_t __convention("regparm") sub_2657(int32_t arg1, int16_t arg2, void* arg3 @ edi)
{
    int32_t eflags;
    __out_dx_al(arg2, arg1, eflags);
    int32_t entry_ebx;
    arg1 = *(entry_ebx + arg1);
    __in_oeax_dx(arg2, eflags);
    *(arg3 - 0x40f4f781) += 1;
    /* jump -> entry_ebx */
}

int32_t sub_266e()
{
    /* undefined */
}

int32_t sub_2681(int32_t arg1 @ ebp, int32_t arg2 @ edi)
{
    *0x4d8aff1a;
    /* tailcall */
    return sub_266e();
}

int32_t __convention("regparm") sub_26b1(int32_t* arg1, int32_t arg2, int32_t arg3, void* arg4 @ edi)
{
    int32_t eflags;
    int32_t eflags_1;
    char temp0_3;
    char temp1_1;
    temp0_3 = __aas(arg1, *(&arg1 + 1), eflags);
    arg1 = temp0_3;
    *(&arg1 + 1) = temp1_1;
    char temp0_2;
    char temp1;
    
    while (true)
    {
        arg1 = __in_al_dx(arg2, eflags_1);
        arg1 = __salc(eflags_1);
        int32_t esp;
        *(esp - 4) = arg3;
        temp0_2 = *(&arg3 + 1);
        temp1 = *0xe9d615a0;
        *(&arg3 + 1) += *0xe9d615a0;
        
        if (temp0_2 <= -(temp1))
            break;
        
        *(esp - 8) = arg4;
        esp -= 8;
        *arg1 += arg1;
    }
    
    if (temp0_2 != -(temp1) && arg3 == 1)
        /* tailcall */
        return sub_26c9(arg1, arg2, arg4);
    
    *(arg3 - 1) ^= arg1;
    __out_immb_al(0xd6, arg1, eflags_1);
    __in_oeax_immb(0xf, eflags_1);
    /* undefined */
}

int32_t __convention("regparm") sub_26c9(int32_t arg1, int32_t arg2, void* arg3 @ edi)
{
    *arg3;
    uint32_t* edi = arg3 + 4;
    *edi u>>= 0xa0;
    
    if ((arg1 | *(arg2 - 0x32)) > 0)
        /* undefined */
    
    /* tailcall */
    return sub_26d2();
}

int32_t sub_26d2()
{
    int32_t entry_ebx;
    /* jump -> *(entry_ebx + 0xb1c08ee1) */
}

void sub_26fb(int32_t arg1 @ edi) __noreturn
{
    *(arg1 - 0x7b54fabf);
    breakpoint();
}

int32_t __convention("fastcall") sub_2ae0(int32_t arg1, int16_t arg2)
{
    int32_t var_4 = arg1;
    void* eax = *0xffffaaee;
    bool c;
    *(&arg2 + 1) = *(&arg2 + 1) - arg1;
    *(eax + 0x25) = eax;
    int16_t entry_ebx;
    *(&entry_ebx + 1) |= entry_ebx;
    int32_t eflags;
    eax = __in_al_dx(arg2, eflags);
    arg2 &= *(&entry_ebx + 1);
    /* undefined */
}

int32_t sub_2b14(int32_t* arg1 @ edi)
{
    int32_t eax;
    int32_t ecx;
    void* edx;
    int32_t esi;
    eax = (*(esi + 0x38))();
    int32_t var_4 = 0x2b;
    int32_t eflags;
    eax = __salc(eflags);
    bool z;
    
    if (!z && ecx != 1)
    {
        *arg1 -= 1;
        bool c;
        *(edx + 0x4dfee092) = *(edx + 0x4dfee092) - edx;
    }
    
    *0xc3cb7f7f;
    /* undefined */
}

int32_t sub_2b4c(void* arg1 @ ebp, void* arg2 @ esi, char* arg3 @ edi)
{
    int32_t eax;
    int32_t ecx;
    int32_t edx;
    eax = ecx();
    int32_t temp1 = *(arg3 + 0x50);
    *(arg3 + 0x50) += 1;
    bool p = /* bool p = unimplemented  {inc dword [edi+0x50]} */;
    bool a = /* bool a = unimplemented  {inc dword [edi+0x50]} */;
    bool z = temp1 == 0xffffffff;
    bool s = temp1 + 1 < 0;
    bool o = temp1 + 1;
    int32_t* esp;
    
    if (z || s != o)
        esp = *(arg1 + 0x5d92c7ff);
    
    while (!z && s == o)
    {
        *arg3 = *(arg2 - 1);
        void* edi = &arg3[4];
        arg2 += 3;
        arg3 = edi + 1;
        p = /* p = unimplemented  {inc edi} */;
        a = /* a = unimplemented  {inc edi} */;
        z = edi == 0xffffffff;
        s = edi + 1 < 0;
        o = edi + 1;
        int32_t temp0_1 = edx;
        edx = eax;
        eax = temp0_1;
        *esp;
        esp = &esp[1];
    }
    
    bool c;
    *(&eax + 1) =
        (s ? 1 : 0) << 7 | (z ? 1 : 0) << 6 | (a ? 1 : 0) << 4 | (p ? 1 : 0) << 2 | (c ? 1 : 0);
    *arg3 = eax;
    int32_t* edi_1 = &arg3[1];
    void* entry_ebx;
    *(&entry_ebx + 1) = *(&entry_ebx + 1);
    (*eax)();
    int16_t ds;
    *(esp - 4) = ds;
    *(entry_ebx - 5);
    edi_1[0x1105283c] -= 1;
    int32_t eax_1;
    
    while (true)
    {
        int32_t temp3_1 = *edi_1;
        *edi_1 += 1;
        
        if (!(temp3_1 + 1))
            break;
        
        eax_1 = 9 + 0x44;
        c = 9 + 0x44 < 9 || (c && 9 + 0x44 == 9);
    }
    
    *0x2ff8911e = 0xff454909;
    int32_t eflags;
    eax_1 = __in_al_immb(0xf2, eflags);
    *edi_1;
    /* undefined */
}

int32_t __convention("regparm") sub_2b82(int16_t arg1)
{
    int32_t eflags;
    int32_t eflags_1;
    char temp0_1;
    char temp1_1;
    temp0_1 = __aas(arg1, *(&arg1 + 1), eflags);
    arg1 = temp0_1;
    *(&arg1 + 1) = temp1_1;
    0xf8b31b9b();
    int32_t ebp;
    int32_t var_2_1 = ebp;
    *0x2ef81250;
    int32_t eax_1;
    int16_t edx;
    int32_t edi;
    eax_1 = (*(edi - 0x57410c01))();
    return eax_1 + 0x5b829a6c;
}

int32_t __convention("regparm") sub_2bc5(void* arg1, int16_t arg2, int32_t arg3 @ ebp)
{
    bool c;
    arg2 = arg2 + *(&arg2 + 1);
    
    if (arg1 != 0xd95210fb && arg1 < 0xd95210fb)
        /* undefined */
    
    /* tailcall */
    return sub_2bce(arg1 + 0x26adef05, arg2);
}

int32_t __convention("regparm") sub_2bce(void* arg1, int16_t arg2)
{
    *(&arg2 + 1) -= *(arg1 - 0xb804);
    *(arg1 + 0x330c3f27) &= 0xa8;
    char* eax = arg1 | 0x87ffa182;
    char* var_4 = eax;
    *eax = ~*eax;
    int16_t eax_1;
    void* entry_ebx;
    *(&eax_1 + 1) = *(&(eax & 0xd8b2) + 1) + *(entry_ebx - 0x2026ec08);
    /* undefined */
}

void __convention("regparm") sub_2e80(char arg1, int16_t arg2) __noreturn
{
    int32_t eflags;
    __out_dx_al(arg2, arg1, eflags);
    int32_t ebx;
    ebx = 0x10;
    trap(0xd);
}

long double __convention("regparm") sub_33ce(double* arg1, int32_t arg2, int32_t arg3, void* arg4 @ ebp, int32_t arg5 @ edi, long double arg6 @ st0)
{
    int32_t var_4 = *(arg2 + arg4 + 0x4a);
    int32_t* esp = &var_4;
    long double result = arg6 / *arg1;
    int32_t eax = COMBINE(arg2, arg1) / arg5;
    bool s;
    bool o;
    
    while (o)
    {
        *(&eax + 1) += *(arg4 - 2);
        *(arg4 - 2);
        int32_t temp4_1 = *(eax + (arg3 << 2));
        *(eax + (arg3 << 2)) += 1;
        s = temp4_1 + 1 < 0;
        o = temp4_1 + 1;
        
        if (o)
            return result;
    }
    
    while (true)
    {
        *(esp - 4) = arg3;
        __ud0_gpr32_gpr32(0x8e5213f8, 0x8e5213f8);
        
        if (!s)
            break;
        
        *(esp - 8) = COMBINE(arg2, arg1) % arg5;
        esp -= 8;
    }
    
    /* undefined */
}

int32_t __convention("regparm") sub_33f2(int32_t arg1, int32_t arg2, void* arg3 @ esi, uint32_t arg4 @ edi)
{
    *(arg3 - 0x7c16008) += 1;
    int32_t eflags;
    int32_t eflags_1;
    char temp0;
    char temp1;
    temp0 = __aas(arg1, *(&arg1 + 1), eflags);
    arg1 = temp0;
    *(&arg1 + 1) = temp1;
    void* ecx;
    ecx = 0xef;
    int32_t temp2 = *(ecx + 0x52);
    int32_t edx = arg2 + *(ecx + 0x52);
    
    while (true)
    {
        int32_t esp;
        *(esp - 4) = ecx;
        __ud0_gpr32_gpr32(arg4, arg4);
        
        if (arg2 + temp2 >= 0)
            break;
        
        *(esp - 8) = edx;
        esp -= 8;
    }
    
    /* undefined */
}

int32_t __convention("regparm") sub_3414(char arg1)
{
    int32_t eflags;
    __cli(eflags);
    int32_t edi;
    int32_t var_4 = edi;
    bool c;
    return arg1 - 0x2c;
}

void __convention("regparm") sub_341a(int32_t arg1) __noreturn
{
    int32_t eflags;
    int32_t eflags_1;
    char temp0_1;
    temp0_1 = __das(arg1, eflags);
    arg1 = temp0_1;
    breakpoint();
}

long double __convention("fastcall") sub_34d5(int32_t arg1, int32_t arg2 @ ebp, int32_t* arg3 @ esi, int32_t arg4 @ edi, long double arg5 @ st0)
{
    *arg3 -= arg1;
    int32_t eflags;
    __salc(eflags);
    int16_t cs;
    (*(arg2 - 0x16))(0xffffffce, cs);
    int32_t entry_ebx;
    *entry_ebx;
    return arg5 - arg5;
}

int32_t __convention("regparm") sub_368e(int32_t arg1, uint16_t arg2, int32_t arg3 @ esi)
{
    arg1 ^= 0x27;
    *(arg3 + 0x2a430353);
    int32_t eflags;
    __out_dx_oeax(arg2, arg1, eflags);
    /* jump -> *arg1 */
}

int32_t sub_3daf(int32_t arg1 @ esi)
{
    int32_t var_4 = *(arg1 * 9 + 0x5f);
    bool p;
    
    if (p)
        /* undefined */
    
    char ecx;
    char* edi;
    /* tailcall */
    return sub_3db5(ecx, edi);
}

char __convention("fastcall") sub_3db5(char arg1, char* arg2 @ edi)
{
    *arg2 ^= arg1;
    int32_t eflags;
    char temp0;
    char temp1;
    bool c;
    temp0 = __aam_immb(0x9a, 0x8975ecfe - 0x470201);
    char result;
    *(&result + 1) = temp1;
    return result;
}

int32_t __convention("regparm") sub_4119(int16_t arg1, int32_t, char arg3, void* arg4 @ edi)
{
    int32_t eflags;
    int32_t eflags_1;
    char temp0;
    char temp1;
    temp0 = __aas((arg1 + 1), *(&(arg1 + 1) + 1), eflags);
    int16_t result;
    result = temp0;
    *(&result + 1) = temp1;
    *(arg4 - 0x1e0910c) ^= arg3;
    return result;
}

int32_t __convention("regparm") sub_413c(int32_t arg1, int32_t arg2, int32_t arg3 @ edi)
{
    /* undefined */
}

int32_t __convention("regparm") sub_4146(char arg1)
{
    int32_t var_4 = 0x3f;
    /* undefined */
}

void __convention("regparm") sub_4163(int16_t arg1, int32_t, char arg3) __noreturn
{
    *(&arg1 + 1) ^= arg3;
    void* entry_ebx;
    *(entry_ebx - 0x4df38781) = ROLB(*(entry_ebx - 0x4df38781), 0xff);
    breakpoint();
}

void __convention("fastcall") sub_8580(void* arg1) __noreturn
{
    arg1 = arg1;
    *(&arg1 + 1) |= *(arg1 + 0x1c1faa7a);
    trap(0xd);
}

int32_t sub_a433() __pure
{
    return;
}

int32_t sub_a43d(int32_t* arg1 @ esi, int32_t arg2 @ edi)
{
    bool c;
    bool p;
    bool a;
    bool z;
    bool s;
    bool d;
    bool o;
    int32_t var_4 = (o ? 1 : 0) << 0xb | (d ? 1 : 0) << 0xa | (s ? 1 : 0) << 7 | (z ? 1 : 0) << 6
        | (a ? 1 : 0) << 4 | (p ? 1 : 0) << 2 | (c ? 1 : 0);
    *arg1;
    /* undefined */
}

int32_t j_sub_a43d(int32_t* arg1 @ esi, int32_t arg2 @ edi)
{
    /* tailcall */
    return sub_a43d(arg1, arg2);
}

int32_t sub_a4c8()
{
    int32_t ecx;
    ecx = 0x72;
    /* undefined */
}

int32_t __convention("regparm") sub_a4cc(int16_t arg1, int32_t arg2, int32_t arg3, int32_t arg4 @ esi)
{
    int16_t entry_ebx;
    *(&entry_ebx + 1) -= *(&arg1 + 1);
    /* jump -> *(arg4 + 0xe81f0159) */
}

