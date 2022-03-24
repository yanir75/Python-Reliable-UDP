import time


class CC:
    def __init__(self):
        # maximum window size since the last decrement
        self.wLast_max = 0
        # start time since last packet loss/timeout
        self.epoch_start = 0
        # start of the window size since last packet loss/timeout
        self.origin_point = 0
        # The timeout value for the last packet
        self.dMin = 0
        # Parmeter to calculate the window size of tcp friendliness
        self.w_TCP = 0
        # Cubic parameter
        self.K = 0
        # ack counter
        self.ack_count = 0
        # friendliness and convergence activated
        self.tcp_friendliness = 1
        self.fast_convergence = 1
        # congestion window
        self.cwnd = 1
        # constants
        self.B = 0.2
        self.C = 0.4
        # slow start threshold
        self.ssThresh = 100
        # update parameters of continues acks after we surpassed the slow start threshold
        self.cwndcount = 0
        # number of continuous ack
        self.continuos_ack = 0

    def ack_recv(self, RTT):
        self.continuos_ack += 1
        if self.continuos_ack == self.ssThresh/2:
            self.ssThresh += self.continuos_ack/4
            self.continuos_ack = 0
        # update timeout according to RTT
        if self.dMin:
            self.dMin = min(self.dMin, RTT * 4)
        else:
            self.dMin = RTT * 4
        if self.cwnd <= self.ssThresh:
            self.cwnd += 1
        else:
            # update window after ssThresh
            cnt = self.cubic_update()
            if self.cwndcount > cnt:
                self.cwnd += 1
                self.cwndcount = 0
            else:
                self.cwndcount += 1

    def packet_loss(self):
        # update the parameters on a packet loss
        self.continuos_ack = 0
        self.epoch_start = 0
        # last maximum window size in FC we want it to be a bit bigger than the current window size
        if self.cwnd < self.wLast_max and self.fast_convergence:
            self.wLast_max = self.cwnd * (2 - self.B) / 2
        else:
            # update the parameters on a packet loss
            self.wLast_max = self.cwnd
            self.ssThresh = self.cwnd
            self.cwnd = self.cwnd * (1 - self.B)

    def cubic_update(self):
        # on ack count we update the count by 1
        self.ack_count += 1
        # if the epoch time = 0 means we lost a packet and we update it to be the current time
        if self.epoch_start <= 0:
            self.epoch_start = time.time()
            if self.cwnd < self.wLast_max:
                # if the window is smaller than the max window size we update the K paramter of cubic and the origin point
                self.K = ((self.wLast_max - self.cwnd) / self.C) ** (1 / 3)
                self.origin_point = self.wLast_max
            else:
                # Update k to be 0 since we need to update that parameter
                self.K = 0
                # update the origin point to the window size since its bigger than the last maximum window size
                self.origin_point = self.cwnd
            self.ack_count = 1
            self.w_TCP = self.cwnd
        # we update the parameters according to cubic (calculations of the time and the origin point and the K parameter)
        t = self.dMin/4 + time.time() - self.epoch_start
        target = self.origin_point + self.C * ((t - self.K) ** 3)
        # the target is larger than self.cwnd we update the cwnd
        if target > self.cwnd:
            cnt = self.cwnd / (target - self.cwnd)
        else:
            cnt = 100 * self.cwnd
        # activate tcp friendliness
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
        # Changes the parameters
        # updates the last max window size
        self.wLast_max = self.cwnd
        # updates the ssThresh
        self.ssThresh = max(2, int(self.cwnd * self.B))
        # updates the window size
        self.cwnd = self.cwnd * (1 - self.B)
        # updates the timeout
        self.dMin = self.dMin * 3
