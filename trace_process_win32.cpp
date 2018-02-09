// Simple harness for tracing a Win32 program from CreateProcess under Reven 
// @richinseattle


#include <windows.h>
#include <stdio.h>

void start_vm()
{
    __asm
    {
        mov  eax, 0xeff1cad6
        mov  edx, 0xdeadbabe
        int 3
    }
}

void stop_vm()
{
    __asm
    {
        mov  eax, 0xeff1cad1
        mov  edx, 0xdeadbabe
        int 3
    }
}

bool run_target(char *cmdline)
{
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory( &si, sizeof(si) );
    si.cb = sizeof(si);
    ZeroMemory( &pi, sizeof(pi) );

    if(!CreateProcess( 
        NULL,           // No module name (use command line)
        cmdline,        // Command line
        NULL,           // Process handle not inheritable
        NULL,           // Thread handle not inheritable
        FALSE,          // Set handle inheritance to FALSE
        0,              // No creation flags
        NULL,           // Use parent's environment block
        NULL,           // Use parent's starting directory 
        &si,            // Pointer to STARTUPINFO structure
        &pi)            // Pointer to PROCESS_INFORMATION structure
    ) 
    {
        printf("CreateProcess failed (%d)\n", GetLastError());
        return false;
    }
    return true;
}

int main(int argc, char **argv)
{
    if(argc < 2)
    {
        printf("Usage: %s [cmdline]\n", argv[0]);
        return 0;
    }

    // run target once without tracing to get it into memory
    // this is done to reduce amount of work recorded in trace
    // NOTE: pass an extra argument to skip this step
    if(argc < 3 && !run_target(argv[1])) return 1;

    // run target again under reven trace
    start_vm();
    run_target(argv[1]);
    stop_vm();

    return 0;
}
