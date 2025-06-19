// omp.h - Simplified mock OpenMP header for demonstration purposes
#ifndef _OMP_H
#define _OMP_H

#ifdef __cplusplus
extern "C" {
#endif

// Basic OpenMP functions we need
inline int omp_get_thread_num() { return 0; }
inline int omp_get_num_threads() { return 1; }
inline void omp_set_num_threads(int num_threads) { /* Does nothing in mock */ }

// Define the most common OpenMP macros
#define _OPENMP 201511
#define OMP_PROC_BIND_FALSE 0
#define OMP_PROC_BIND_TRUE 1
#define OMP_PROC_BIND_MASTER 2
#define OMP_PROC_BIND_CLOSE 3
#define OMP_PROC_BIND_SPREAD 4

// Define pragma replacements (these won't do anything, but will compile)
#define _Pragma(x)
#define omp parallel for
#define omp parallel
#define omp for

#ifdef __cplusplus
}
#endif

#endif /* _OMP_H */