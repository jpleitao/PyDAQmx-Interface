import threading


class SFC:

    def __init__(self):
        pass


class ControllerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.feedback_list = []
        self.setpoint_list = []
        self.output_list = []
        self.time_sm = []
        self.time_list = []
        self.feedback_smooth = []
        self.completed = False
        self.failed = {"status": False, "reason": ""}
        self.type = "SFC"
        self.abort = False
        self.flip = -1

    def run(self):
        try:
            self.completed = True
        except Exception, msg:
            self.failed["status"] = True
            self.failed["reason"] = msg


"""if __name__ == "__main__":
    SAMPLES = 10
    my_reader = daqmxlib.Reader({"ai0": 1})
    my_actuator = daqmxlib.Actuator(["ao0"])
    my_actuator.execute_task("ao0", 1, 0)
    time.sleep(1)
    controller_thread = ControllerThread(my_reader, my_actuator, "", P=2, I=1, D=0, SETPOINT=3, TS=0.05,
                                         SAMPLES=SAMPLES)
    controller_thread.start()
    controller_thread.join()
    # print controller_thread.feedback_smooth

    if controller_thread.completed:
        plt.plot(controller_thread.time_smooth, controller_thread.feedback_smooth)
        plt.plot(controller_thread.time_smooth, controller_thread.output_smooth)
        plt.plot(controller_thread.time_list, controller_thread.setpoint_list)
        plt.xlim((0, SAMPLES))
        plt.ylim(-10, 10)
        # plt.ylim((min(controller_thread.feedback_list) - 0.5, max(controller_thread.feedback_list) + 0.5))
        plt.xlabel('time (s)')
        plt.ylabel('PID (PV)')
        plt.title('TEST PID')

        plt.grid(True)
        plt.show()"""
