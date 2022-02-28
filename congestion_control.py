import time


class CC:
    def __init__(self):
        self.wLast_max = 0
        self.epoch_start = 0
        self.origin_point = 0
        self.dMin = 0
        self.w_TCP = 0
        self.K = 0
        self.ack_count = 0
        self.tcp_friendliness = 1
        self.fast_convergence = 1
        self.cwnd = 1
        self.B = 0.2
        self.C = 0.4
        self.ssThresh = 100
        self.cwndcount = 0

    def ack_recv(self, RTT):
        if self.dMin:
            self.dMin = min(self.dMin, RTT * 4)
        else:
            self.dMin = RTT * 4
        if self.cwnd <= self.ssThresh:
            self.cwnd += 1
        else:
            cnt = self.cubic_update()
            if self.cwndcount > cnt:
                self.cwnd += 1
                self.cwndcount = 0
            else:
                self.cwndcount += 1

    def packet_loss(self):
        self.epoch_start = 0
        if self.cwnd < self.wLast_max and self.fast_convergence:
            self.wLast_max = self.cwnd * (2 - self.B) / 2
        else:
            self.wLast_max = self.cwnd
            self.ssThresh = self.cwnd
            self.cwnd = self.cwnd * (1 - self.B)

    def timeout(self):
        self.cubic_reset()

    def cubic_update(self):
        self.ack_count += 1
        if self.epoch_start <= 0:
            self.epoch_start = time.time()
            if self.cwnd < self.wLast_max:
                self.K = ((self.wLast_max - self.cwnd) / self.C) ** (1 / 3)
                self.origin_point = self.wLast_max
            else:
                self.K = 0
                self.origin_point = self.cwnd
            self.ack_count = 1
            self.w_TCP = self.cwnd
        t = self.dMin + time.time() - self.epoch_start
        target = self.origin_point + self.C * ((t - self.K) ** 3)
        if target > self.cwnd:
            cnt = self.cwnd / (target - self.cwnd)
        else:
            cnt = 100 * self.cwnd
        if self.tcp_friendliness:
            cnt = self.cubic_tcp_friendliness(cnt)
        return cnt

    def cubic_tcp_friendliness(self, cnt):
        self.w_TCP = self.w_TCP + (3 * self.B / (2 - self.B)) * (self.ack_count / self.cwnd)
        self.ack_count = 0
        if self.w_TCP > self.cwnd:
            max_cnt = self.cwnd / (self.w_TCP - self.cwnd)
            if cnt > max_cnt:
                cnt = max_cnt
        return cnt

    def double_ack(self):
        self.wLast_max = self.cwnd
        self.ssThresh = max(2, int(self.cwnd * self.B))
        self.cwnd = self.cwnd * (1 - self.B)

    def cubic_reset(self):
        self.wLast_max = 0
        self.epoch_start = 0
        self.origin_point = 0
        self.dMin = 0
        self.w_TCP = 0
        self.K = 0
        self.ack_count = 0
