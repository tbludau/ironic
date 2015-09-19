# Copyright 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_utils import importutils

from ironic.common import exception
from ironic.common.i18n import _
from ironic.drivers import base
from ironic.drivers.modules import agent
from ironic.drivers.modules import ipminative
from ironic.drivers.modules import ipmitool
from ironic.drivers.modules import pxe
from ironic.drivers.modules import ssh
from ironic.drivers.modules.ucs import management as ucs_mgmt
from ironic.drivers.modules.ucs import power as ucs_power
from ironic.drivers.modules import virtualbox
from ironic.drivers import utils


class AgentAndIPMIToolDriver(base.BaseDriver):
    """Agent + IPMITool driver.

    This driver implements the `core` functionality, combining
    :class:`ironic.drivers.modules.ipmitool.IPMIPower` (for power on/off and
    reboot) with :class:`ironic.drivers.modules.agent.AgentDeploy` (for
    image deployment).
    Implementations are in those respective classes; this class is merely the
    glue between them.
    """

    def __init__(self):
        self.power = ipmitool.IPMIPower()
        self.boot = pxe.PXEBoot()
        self.deploy = agent.AgentDeploy()
        self.management = ipmitool.IPMIManagement()
        self.console = ipmitool.IPMIShellinaboxConsole()
        self.agent_vendor = agent.AgentVendorInterface()
        self.ipmi_vendor = ipmitool.VendorPassthru()
        self.mapping = {'send_raw': self.ipmi_vendor,
                        'bmc_reset': self.ipmi_vendor,
                        'heartbeat': self.agent_vendor}
        self.driver_passthru_mapping = {'lookup': self.agent_vendor}
        self.vendor = utils.MixinVendorInterface(
            self.mapping,
            driver_passthru_mapping=self.driver_passthru_mapping)
        self.raid = agent.AgentRAID()


class AgentAndIPMINativeDriver(base.BaseDriver):
    """Agent + IPMINative driver.

    This driver implements the `core` functionality, combining
    :class:`ironic.drivers.modules.ipminative.NativeIPMIPower` (for power
    on/off and reboot) with
    :class:`ironic.drivers.modules.agent.AgentDeploy` (for image
    deployment).
    Implementations are in those respective classes; this class is merely the
    glue between them.
    """

    def __init__(self):
        self.power = ipminative.NativeIPMIPower()
        self.boot = pxe.PXEBoot()
        self.deploy = agent.AgentDeploy()
        self.management = ipminative.NativeIPMIManagement()
        self.console = ipminative.NativeIPMIShellinaboxConsole()
        self.agent_vendor = agent.AgentVendorInterface()
        self.ipminative_vendor = ipminative.VendorPassthru()
        self.mapping = {
            'send_raw': self.ipminative_vendor,
            'bmc_reset': self.ipminative_vendor,
            'heartbeat': self.agent_vendor,
        }
        self.driver_passthru_mapping = {'lookup': self.agent_vendor}
        self.vendor = utils.MixinVendorInterface(self.mapping,
                                                 self.driver_passthru_mapping)
        self.raid = agent.AgentRAID()


class AgentAndSSHDriver(base.BaseDriver):
    """Agent + SSH driver.

    NOTE: This driver is meant only for testing environments.

    This driver implements the `core` functionality, combining
    :class:`ironic.drivers.modules.ssh.SSH` (for power on/off and reboot of
    virtual machines tunneled over SSH), with
    :class:`ironic.drivers.modules.agent.AgentDeploy` (for image
    deployment). Implementations are in those respective classes; this class
    is merely the glue between them.
    """

    def __init__(self):
        self.power = ssh.SSHPower()
        self.boot = pxe.PXEBoot()
        self.deploy = agent.AgentDeploy()
        self.management = ssh.SSHManagement()
        self.vendor = agent.AgentVendorInterface()
        self.raid = agent.AgentRAID()


class AgentAndVirtualBoxDriver(base.BaseDriver):
    """Agent + VirtualBox driver.

    NOTE: This driver is meant only for testing environments.

    This driver implements the `core` functionality, combining
    :class:`ironic.drivers.modules.virtualbox.VirtualBoxPower` (for power
    on/off and reboot of VirtualBox virtual machines), with
    :class:`ironic.drivers.modules.agent.AgentDeploy` (for image
    deployment). Implementations are in those respective classes; this class
    is merely the glue between them.
    """

    def __init__(self):
        if not importutils.try_import('pyremotevbox'):
            raise exception.DriverLoadError(
                driver=self.__class__.__name__,
                reason=_("Unable to import pyremotevbox library"))
        self.power = virtualbox.VirtualBoxPower()
        self.boot = pxe.PXEBoot()
        self.deploy = agent.AgentDeploy()
        self.management = virtualbox.VirtualBoxManagement()
        self.vendor = agent.AgentVendorInterface()
        self.raid = agent.AgentRAID()


class AgentAndUcsDriver(base.BaseDriver):
    """Agent + Cisco UCSM driver.

    This driver implements the `core` functionality, combining
    :class:ironic.drivers.modules.ucs.power.Power for power
    on/off and reboot with
    :class:'ironic.driver.modules.agent.AgentDeploy' (for image deployment.)
    Implementations are in those respective classes;
    this class is merely the glue between them.
    """

    def __init__(self):
        if not importutils.try_import('UcsSdk'):
            raise exception.DriverLoadError(
                driver=self.__class__.__name__,
                reason=_("Unable to import UcsSdk library"))
        self.power = ucs_power.Power()
        self.boot = pxe.PXEBoot()
        self.deploy = agent.AgentDeploy()
        self.management = ucs_mgmt.UcsManagement()
        self.vendor = agent.AgentVendorInterface()
