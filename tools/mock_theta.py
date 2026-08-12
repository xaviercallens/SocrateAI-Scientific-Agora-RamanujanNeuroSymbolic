import sys

def q_pochhammer(a, n, max_N):
    # (a; q)_n = (1-a)(1-aq)...(1-aq^{n-1})
    res = [0]*max_N
    res[0] = 1
    for i in range(n):
        # multiply by (1 - a q^i)
        next_res = list(res)
        for j in range(max_N):
            if j + i < max_N:
                # a q^i corresponds to shift by i
                next_res[j+i] += res[j] * (-a)
        res = next_res
    return res

def poly_add(A, B):
    return [a+b for a,b in zip(A,B)]

def poly_mul(A, B):
    N = len(A)
    C = [0]*N
    for i in range(N):
        for j in range(N-i):
            C[i+j] += A[i]*B[j]
    return C

def poly_inv(A):
    N = len(A)
    B = [0]*N
    B[0] = 1
    for n in range(1, N):
        s = sum(A[k]*B[n-k] for k in range(1, n+1))
        B[n] = -s
    return B

def f_q(N):
    res = [0]*N
    for n in range(N):
        if n*n >= N: break
        # q^{n^2} / (-q; q)_n^2
        num = [0]*N
        num[n*n] = 1
        den = q_pochhammer(-1, n, N) # (-q; q)_n means a=-q, wait!
        # Actually (-q; q)_n = (1+q)(1+q^2)...(1+q^n)
        den = [0]*N
        den[0] = 1
        for i in range(1, n+1):
            nxt = list(den)
            for j in range(N):
                if j+i < N: nxt[j+i] += den[j]
            den = nxt
        den_sq = poly_mul(den, den)
        den_inv = poly_inv(den_sq)
        term = poly_mul(num, den_inv)
        res = poly_add(res, term)
    return res

print(f"f(q): {f_q(10)}")

# phi(q) = sum_{n} q^{n^2} / (-q^2; q^2)_n
def phi_q(N):
    res = [0]*N
    for n in range(N):
        if n*n >= N: break
        num = [0]*N
        num[n*n] = 1
        den = [0]*N
        den[0] = 1
        for i in range(1, n+1):
            nxt = list(den)
            for j in range(N):
                if j+2*i < N: nxt[j+2*i] += den[j]
            den = nxt
        den_inv = poly_inv(den)
        res = poly_add(res, poly_mul(num, den_inv))
    return res

print(f"phi(q): {phi_q(10)}")

# psi(q) = sum_{n} q^{n^2} / (q; q^2)_n
def psi_q(N):
    res = [0]*N
    for n in range(N):
        if n*n >= N: break
        num = [0]*N
        num[n*n] = 1
        den = [0]*N
        den[0] = 1
        for i in range(n):
            nxt = list(den)
            for j in range(N):
                if j+2*i+1 < N: nxt[j+2*i+1] -= den[j]
            den = nxt
        den_inv = poly_inv(den)
        res = poly_add(res, poly_mul(num, den_inv))
    return res

print(f"psi(q): {psi_q(10)}")
