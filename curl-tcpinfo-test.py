
from collections import namedtuple
import struct


TcpInfo = namedtuple("TCP_INFO", r"""
                     tcpi_state
                     tcpi_ca_state
                     tcpi_retransmits
                     tcpi_probes
                     tcpi_backoff
                     tcpi_options
                     tcpi_snd_wscale_and_tcpi_rcv_wscale

                     tcpi_rto
                     tcpi_ato
                     tcpi_snd_mss
                     tcpi_rcv_mss

                     tcpi_unacked
                     tcpi_sacked
                     tcpi_lost
                     tcpi_retrans
                     tcpi_fackets

                     tcpi_last_data_sent
                     tcpi_last_ack_sent
                     tcpi_last_data_recv
                     tcpi_last_ack_recv

                     tcpi_pmtu
                     tcpi_rcv_ssthresh
                     tcpi_rtt
                     tcpi_rttvar
                     tcpi_snd_ssthresh
                     tcpi_snd_cwnd
                     tcpi_advmss
                     tcpi_reordering

                     tcpi_rcv_rtt
                     tcpi_rcv_space

                     tcpi_total_retrans

                     tcpi_pacing_rate
                     tcpi_max_pacing_rate
                     tcpi_bytes_acked
                     tcpi_bytes_received
                     tcpi_segs_out
                     tcpi_segs_in""")
 



    def _unpack(self, tcpinfo):
        """Internal, unpacks the kernel bytearray into something presentable"""

        # TCP_INFO struct in linux 4.2
        fmt = "7B24I4Q2I"  # see /usr/include/linux/tcp.h for details
        padsize = struct.calcsize(fmt)
        # On older kernels, we get fewer bytes, pad with null to fit
        padded = tcpinfo.ljust(padsize, b'\0')
        unpacked = struct.unpack(fmt, padded)
        return TcpInfo._make(unpacked)

    def socket_stats(self):
        """Returns a namedtuple representing TCP_INFO data from kernel. Or None
        if we don't have a socket"""
        sockfd = self._curl.getinfo(self._curl.LASTSOCKET)
        if sockfd > 0:
            sock = socket.socket(fileno=sockfd)
            opt = sock.getsockopt(socket.SOL_TCP, socket.TCP_INFO, 200)
            return self._unpack(opt)
        else:
            return None
