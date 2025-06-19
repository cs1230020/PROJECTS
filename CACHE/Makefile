CXX = g++
CXXFLAGS = -std=c++17 -O2 -w
LDFLAGS = 

SRCS = main.cpp Cache.cpp CacheLine.cpp CacheSet.cpp Processor.cpp Bus.cpp Simulator.cpp TraceReader.cpp Statistics.cpp
OBJS = $(SRCS:.cpp=.o)
TARGET = L1simulate

# Trace generation files
TRACE_SRCS = matrix_vector_mult.cpp
TRACE_TARGET = matrix_trace_gen

.PHONY: all clean trace

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(LDFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Rule to build and run the trace generator
trace: $(TRACE_TARGET)
	./$(TRACE_TARGET)

$(TRACE_TARGET): $(TRACE_SRCS)
	$(CXX) $(CXXFLAGS) -o $@ $^

clean:
	rm -f $(OBJS) $(TARGET) $(TRACE_TARGET) matmul_proc*.trace