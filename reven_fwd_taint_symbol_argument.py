import reven

# Taint a buffer at first occurance of specified symbol and propagate


def read_symbolic(point, symbolic):
    if isinstance(symbolic, reven.SymbolicRegister):
        return point.cpu().read_register(symbolic.name)
    elif isinstance(symbolic, reven.SymbolicPhysicalMemory):
        mem = point.memory().read_physical(symbolic.address, symbolic.size)
        value = 0
        for byte in reversed(mem):
            value <<= 8
            value |= ord(byte)
        return value


def propagate_taint_once(pt, current_taint):
    taint_result = project.taint(pt, current_taint, forward=True, count=1)

    for point, diff in sorted(taint_result.diffs.iteritems()):
        print point
        print "\t taint in:  ", [s.name for s in diff.tainted]
        print "\t taint out: ", [s.name for s in diff.untainted],
        print
        current_taint += diff.tainted
        current_taint = [sym for sym in current_taint if sym not in diff.untainted]
        for sym in diff.untainted:
            current_taint = [s for s in current_taint if s.name != sym.name]
        for sym in current_taint:
            print "%s=0x%x" % (sym.name, read_symbolic(point, sym))
        print

        return current_taint


print "\nReven Taint Trace\n"

# default = "127.0.0.1"
reven_server = os.getenv('REVEN_SERVER') 
if reven_server == None:
    reven_server = "127.0.0.1"

reven_project_port = os.getenv('REVEN_PROJECT_PORT') 
if reven_project_port == None:
    print "ERROR: REVEN_PROJECT_PORT must be set"
    sys.exit(1)

reven_symbol_name = os.getenv('REVEN_SYMBOL_NAME') 
if reven_project_port == None:
    print "ERROR: REVEN_SYMBOL_NAME must be set"
    sys.exit(1)

reven_taint_parameter = os.getenv('REVEN_TAINT_PARAMETER')
if reven_taint_parameter == None:
    print "ERROR: REVEN_TAINT_PARAMETER must be set"
    sys.exit(1)

reven_taint_size = os.getenv('REVEN_TAINT_SIZE')
if reven_taint_size == None:
    print "ERROR: REVEN_TAINT_SIZE must be set"
    sys.exit(1)

reven_taint_iterations = os.getenv('REVEN_TAINT_ITERATIONS')
if reven_taint_iterations == None:
    print "ERROR: REVEN_TAINT_ITERATIONS must be set"
    sys.exit(1)


project = reven.Project(reven_server, reven_project_port)

trace = project.traces()[0]
seq_count = trace.sequence_count
print "Tracing from symbol: %s" % (reven_symbol_name) 
crit = reven.SymbolCriterion(reven_symbol_name, accuracy="exact")
for p in trace.search_point([crit]):
    point = p
    break

print "Beginning taint trace at %s\n" % point.symbol.name
cpu = point.cpu()
mem = point.memory()
esp = cpu.read_register("esp")
tainted_buffer_ptr = mem.read_u32(esp + (4 * REVEN_TAINT_PARAMETER)
print "Found tainted buffer at: 0x%x" % tainted_buffer_ptr
tainted_buffer_physical_addr = mem.get_physical_address(tainted_buffer_ptr)
print "Buffer physical address: 0x%08x\n\n" % tainted_buffer_physical_addr

taint_area = []
for i in range(0, reven_taint_size):
    taint_area.append(reven.SymbolicPhysicalMemory(tainted_buffer_physical_addr + i, 1)])

current_taint = taint_area
print "Propagating taint for %d iterations .. here we go!\n\n" % reven_taint_iterations 
for i in range(0, reven_taint_iterations):
    current_taint = propagate_taint_once(point, current_taint)
    point = point.next()
