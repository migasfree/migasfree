# -*- coding: utf-8 -*-

# import order is very important!!!

from .stats import (
    delay_schedule,
    synchronized_daily,
    synchronized_monthly,
    stats_dashboard,
    provided_computers_by_delay,
)
from .queries import get_query, computer_messages
from .hardware import hardware_resume, hardware_extract, load_hw, process_hw
from .client_api import api
from .public_api import (
    get_projects, get_computer_info, computer_label,
    get_key_repositories, RepositoriesUrlTemplateView,
)
from .packages import info
from .login import login, preferences
from .computer import (
    ComputerDelete,
    computer_delete_selected,
    computer_replacement,
    computer_events,
    computer_change_status,
    computer_simulate_sync,
)
from .migas_link import link
from .timeline import timeline

from .project import ProjectDelete
from .platform import PlatformDelete, platform_delete_selected
from .devices import connections_model, device_replacement
from .autocomplete import (
    ComputerAutocomplete, AttributeAutocomplete,
    DeviceAutocomplete, UserProfileAutocomplete,
    GroupAutocomplete,
)
from .token import (
    ComputerViewSet, ProjectViewSet, PlatformViewSet,
    PmsViewSet, StoreViewSet, PropertyViewSet, AttributeSetViewSet,
    AttributeViewSet, ScheduleViewSet, PackageViewSet,
    DeploymentViewSet, ErrorViewSet, FaultDefinitionViewSet,
    FaultViewSet, NotificationViewSet, MigrationViewSet,
    HardwareComputerViewSet, HardwareViewSet,
    UserViewSet, SynchronizationViewSet, StatusLogViewSet,
)
