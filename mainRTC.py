#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file mainRTC.py
 @brief ModuleDescription
 @date $Date$


"""
# </rtc-template>

import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
mainrtc_spec = ["implementation_id", "mainRTC", 
         "type_name",         "mainRTC", 
         "description",       "ModuleDescription", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Category", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]
# </rtc-template>

# <rtc-template block="component_description">
##
# @class mainRTC
# @brief ModuleDescription
# 
# 
# </rtc-template>
class mainRTC(OpenRTM_aist.DataFlowComponentBase):
	
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_camera_human = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._camera_humanIn = OpenRTM_aist.InPort("camera_human", self._d_camera_human)

        self._d_camera_face = OpenRTM_aist.instantiateDataType(RTC.TimedFloatSeq)
        self._camera_faceIn = OpenRTM_aist.InPort("camera_face", self._d_camera_face)

        self._d_arm_state = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._arm_stateIn = OpenRTM_aist.InPort("arm_state", self._d_arm_state)

        self._d_base_state = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._base_stateIn = OpenRTM_aist.InPort("base_state", self._d_base_state)

        self._d_arm_move = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._arm_moveOut = OpenRTM_aist.OutPort("arm_move", self._d_arm_move)

        self._d_base_move = OpenRTM_aist.instantiateDataType(RTC.TimedFloatSeq)
        self._base_moveOut = OpenRTM_aist.OutPort("base_move", self._d_base_move)

        ### system states
        self._state = "STOP" # STOP -> WAIT_BASE_DONE -> WAIT_ARM_DONE
        self._last_human_flag = False
        self._arm_started = False

        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
		
        # </rtc-template>
		 
    ##
    #
    # The initialize action (on CREATED->ALIVE transition)
    # 
    # @return RTC::ReturnCode_t
    # 
    #
    def onInitialize(self):
        # Bind variables and configuration variable
		
        # Set InPort buffers
        self.addInPort("camera_human",self._camera_humanIn) # x, y, depth, area 
        self.addInPort("camera_face",self._camera_faceIn) # Truth or Falsh
        self.addInPort("arm_state",self._arm_stateIn) # Truth or Falsh
        self.addInPort("base_state",self._base_stateIn) # Truth or Falsh
		
        # Set OutPort buffers
        self.addOutPort("arm_move",self._arm_moveOut) # Truth or Falsh
        self.addOutPort("base_move",self._base_moveOut) # vel
		
        # Set service provider to Ports
		
        # Set service consumers to Ports
		
        # Set CORBA Service Ports
		
        return RTC.RTC_OK
	
    ###
    ## 
    ## The finalize action (on ALIVE->END transition)
    ## 
    ## @return RTC::ReturnCode_t
    #
    ## 
    #def onFinalize(self):
    #

    #    return RTC.RTC_OK
	
    ###
    ##
    ## The startup action when ExecutionContext startup
    ## 
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onStartup(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The shutdown action when ExecutionContext stop
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onShutdown(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ##
    #
    # The activated action (Active state entry action)
    #
    # @param ec_id target ExecutionContext Id
    # 
    # @return RTC::ReturnCode_t
    #
    #
    def onActivated(self, ec_id):
        self._state = "STOP"
        self._last_human_flag = False
        self._arm_started = False
        # rewrite states
        self._write_base(False)
        self._write_arm(False)
        return RTC.RTC_OK
    
    ##
    #
    # The deactivated action (Active state exit action)
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onDeactivated(self, ec_id):
    
        return RTC.RTC_OK
	
    ##
    #
    # Inport and Outport Tool
    #
    def _read_bool(self, inport):
        if inport.isNew():
            data = inport.read()
            return bool(data.data)
        return None

    def _read_seq(self, inport):
        if inport.isNew():
            data = inport.read()
            return list(data.data)
        return None

    def _write_base(self, flag: bool):
        self._d_base_move.data = bool(flag)
        self._base_moveOut.write(self._d_base_move)

    def _write_arm(self, flag: bool):
        self._d_arm_move.data = bool(flag)
        self._arm_moveOut.write(self._d_arm_move)

    ##
    #
    # The execution action that is invoked periodically
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onExecute(self, ec_id):
        # read data
        human_flag = self._read_bool(self._camera_humanIn)
        face_vec = self._read_seq(self._camera_faceIn)
        base_done = self._read_bool(self._base_stateIn)
        arm_done = self._read_bool(self._arm_stateIn)

        # wait for human 
        if human_flag is not None:
            self._last_human_flag = human_flag
            
            # True, move base 
            if human_flag:
                self._write_base(human_flag)
                self._state = "WAIT_BASE_DONE"
            else:
                # False, wait
                if self._state == "STOP":
                    self._write_arm(False)

        # face deteck, arm move
        if self._state == "WAIT_BASE_DONE" and base_done is True:
            arm_go = bool(face_vec and len(face_vec) >= 3) # 3 time face deteck 
            self._write_arm(arm_go)
            self._arm_started = arm_go
            self._state = "WAIT_ARM_DONE" if arm_go else "STOP"

        # end and reset
        if self._state == "WAIT_ARM_DONE" and arm_done is True:
            self._write_arm(False)
            self._write_base(False)
            self._arm_started = False
            self._state = "STOP"

        return RTC.RTC_OK
	
    ###
    ##
    ## The aborting action when main logic error occurred.
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onAborting(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The error action in ERROR state
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onError(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The reset action that is invoked resetting
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onReset(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The state update action that is invoked after onExecute() action
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##

    ##
    #def onStateUpdate(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The action that is invoked when execution context's rate is changed
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onRateChanged(self, ec_id):
    #
    #    return RTC.RTC_OK
	



def mainRTCInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=mainrtc_spec)
    manager.registerFactory(profile,
                            mainRTC,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    mainRTCInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("mainRTC" + args)

def main():
    # remove --instance_name= option
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()

