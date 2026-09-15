from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.values_login_silent_mode import ValuesLoginSilentMode
from ..models.values_search_preview_mode import ValuesSearchPreviewMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.admin import Admin
    from ..models.available_mds import AvailableMds
    from ..models.banner import Banner
    from ..models.collections import Collections
    from ..models.config_frontpage import ConfigFrontpage
    from ..models.config_privacy import ConfigPrivacy
    from ..models.config_publish import ConfigPublish
    from ..models.config_rating import ConfigRating
    from ..models.config_remote import ConfigRemote
    from ..models.config_report_problem import ConfigReportProblem
    from ..models.config_theme_colors import ConfigThemeColors
    from ..models.config_tutorial import ConfigTutorial
    from ..models.config_upload import ConfigUpload
    from ..models.config_workflow import ConfigWorkflow
    from ..models.context_menu_entry import ContextMenuEntry
    from ..models.font_icon import FontIcon
    from ..models.gdpr import Gdpr
    from ..models.help_menu_options import HelpMenuOptions
    from ..models.image import Image
    from ..models.license_ import License
    from ..models.license_agreement import LicenseAgreement
    from ..models.logout_info import LogoutInfo
    from ..models.mainnav import Mainnav
    from ..models.menu_entry import MenuEntry
    from ..models.publishing_config import PublishingConfig
    from ..models.register import Register
    from ..models.relations import Relations
    from ..models.rendering import Rendering
    from ..models.services import Services
    from ..models.session_expired_dialog import SessionExpiredDialog
    from ..models.simple_edit import SimpleEdit
    from ..models.stream import Stream


T = TypeVar("T", bound="Values")


@_attrs_define
class Values:
    """
    Attributes:
        supported_languages (list[str] | Unset): List of supported languages (e.g. 'de', 'en'). First entry is the
            fallback. Only one entry means fallback for all
        extension (str | Unset): Currently a dummy string, not used
        login_url (str | Unset): URL to redirect when login fails (401) or on initial login (e.g. for Shibboleth). Has
            no effect when loginProvidersUrl is set — the providers panel takes precedence.
        login_allow_local (bool | Unset): If loginUrl is set and true, the local login form is shown alongside the
            loginUrl link. When loginProvidersUrl is set and this is explicitly false, the login page shows only the
            providers panel (providers-only mode)
        login_providers_url (str | Unset): URL to a service providing a list of login providers (requires
            loginProviderTargetUrl to be set). When set, the providers panel is always shown and loginUrl redirect is
            suppressed.
        login_provider_target_url (str | Unset): URL called when logging in with a provider. Supports placeholders:
            :target (server URL + loginUrl) and :entity (provider URL)
        login_silent_mode (ValuesLoginSilentMode | Unset): Silent login mode: 'none' (default), 'iframe', or 'redirect'
        register (Register | Unset): Registration settings (local service, custom URLs, password recovery, required
            fields)
        recover_password_url (str | Unset): URL for 'forgot password' link. Empty means button is not shown
        imprint_url (str | Unset): URL to imprint/legal page. Shows button if specified
        privacy_information_url (str | Unset): URL to privacy policy/data protection page. Shows button if specified
        help_url (str | Unset): URL to custom help page (default is edu-sharing help). Empty string hides the button
        whats_new_url (str | Unset): URL to custom 'What's new' page (default is edu-sharing What's new). Empty string
            hides the button
        edit_profile_url (str | Unset): URL where users can edit their profile
        access_denied_info_url (str | Unset): Access denied URL for elements not accessible inside collections
        edit_profile (bool | Unset): Whether user profiles can be edited within edu-sharing (not used if editProfileUrl
            is set)
        workspace_columns (list[str] | Unset): Default displayed columns in workspace
        workspace_shared_to_me_default_all (bool | Unset): Default view for shared materials: false = only direct
            shares, true = all shares
        hide_main_menu (list[str] | Unset): Array of navigation items to hide (e.g. 'workspace', 'search',
            'collections', 'login', 'permissions', 'safe', 'stream')
        logout (LogoutInfo | Unset): Logout configuration (URL, local/SSO-specific URLs, session destruction, AJAX)
        menu_entries (list[MenuEntry] | Unset): Additional custom menu entries in left sidebar (position, icon, name,
            URL/path, scope, etc.)
        custom_options (list[ContextMenuEntry] | Unset): Custom operations for right-click context menu/action bar
            (mode, icon, name, URL with placeholders, permissions)
        user_menu_overrides (list[ContextMenuEntry] | Unset): Custom options for the user menu (shown on username click
            in navigation bar)
        allowed_licenses (list[str] | Unset): Filter license dialog to set of allowed licenses (CC_BY, CC_BY_SA,
            CC_BY_ND, CC_BY_NC, CC_0, PDM, etc.)
        custom_licenses (list[License] | Unset): Define custom licenses (id, position, URL)
        workflow (ConfigWorkflow | Unset): Workflow configuration (default receiver, default status, comment required,
            workflow states)
        license_dialog_on_upload (bool | Unset): If true, show license dialog after file upload
        node_report (bool | Unset): If true, show 'Report problem' option in search results (requires backend
            mail.report.receivers configured)
        branding (bool | Unset): If true (default), show edu-sharing logo top-left and 'Powered by edu-sharing' at login
        rating (ConfigRating | Unset): Rating configuration
        publishing_notice (bool | Unset): If true, show confirmation message when publishing to everyone
        publishing (PublishingConfig | Unset):
        site_title (str | Unset): HTML page title (displayed after environment name). Used if branding is true. Default
            is 'edu-sharing'
        user_display_name (str | Unset): User display name format: 'fullName' (default), 'email', 'firstName',
            'lastName', or 'authorityName'
        user_secondary_display_name (str | Unset): Secondary user name shown below primary name: null (default),
            'authorityName', 'email', or 'email-domain'
        user_affiliation (bool | Unset): If true (default), show user type (teacher, student, etc.) in invite dialog
        default_username (str | Unset): Pre-fill login username for testing
        default_password (str | Unset): Pre-fill login password for testing
        banner (Banner | Unset): Banner configuration (URL, href link, components where shown)
        available_mds (list[AvailableMds] | Unset): Array of allowed metadata sets per repository
        available_repositories (list[str] | Unset): Array of allowed repository IDs. Use '-home-' for local repository
        search_view_type (int | Unset): Default search view type: 0 = list, 1 = tiles (default)
        workspace_view_type (int | Unset): Default workspace view type: 0 = table (default), 1 = tiles
        items_per_request (int | Unset): Number of elements fetched per request cycle (default: 25)
        rendering (Rendering | Unset): Rendering settings (show preview, show download button, prerender content)
        session_expired_dialog (SessionExpiredDialog | Unset): Session expiration dialog configuration
        default_location (str | Unset): Path to navigate to when accessing edu-sharing directly (default: 'login')
        login_default_location (str | Unset): Default landing page after login (default: 'workspace'). Can include query
            parameters like 'collections?scope=EDU_ALL'
        search_group_results (bool | Unset): If true, show repositories separately as lists in 'All' view
        mainnav (Mainnav | Unset): Top navigation bar customization (icon, URL)
        search_sidenav_mode (str | Unset): Metadata search sidebar mode: 'never' (default), 'always', or 'auto' (desktop
            only)
        search_preview_mode (ValuesSearchPreviewMode | Unset): Right sidebar preview mode: show sidebar with optional
            preview, or jump directly to render page
        search_filter_bar_width (int | Unset): Initial width (in pixels) of the search filter bar sidebar. The user may
            still resize it
        collections (Collections | Unset): Collections configuration (allowed colors, special types like editorial)
        license_agreement (LicenseAgreement | Unset): License agreement display settings (node IDs with HTML content per
            language)
        services (Services | Unset): External services configuration
        help_menu_options (list[HelpMenuOptions] | Unset): Custom help menu options (key, icon, URL) - replaces helpUrl
            + whatsNewUrl
        favicon (str | Unset): Favicon URL
        apple_touch_icon (str | Unset): Apple touch icon URL for mobile home screen
        images (list[Image] | Unset): Array of image replacements (src match, replace with)
        icons (list[FontIcon] | Unset): Array of icon identifier replacements (original identifier, replace with)
        stream (Stream | Unset): Stream/activity feed configuration (enabled)
        admin (Admin | Unset): Admin panel configuration
        simple_edit (SimpleEdit | Unset): Quick edit dialog configuration
        frontpage (ConfigFrontpage | Unset): Front page configuration
        upload (ConfigUpload | Unset): File upload configuration
        publish (ConfigPublish | Unset): Publishing configuration
        remote (ConfigRemote | Unset): Remote repository configuration
        report_problem (ConfigReportProblem | Unset): Problem reporting configuration
        custom_css (str | Unset): Custom CSS
        theme_colors (list[ConfigThemeColors] | Unset): Theme color customization. An entry with no theme attribute (or
            theme="light") applies to light mode, theme="dark" to dark mode. A dark entry is used as-is instead of deriving
            dark variants from the light colors client-side
        privacy (ConfigPrivacy | Unset): Privacy settings
        gdpr (Gdpr | Unset): GDPR configuration
        relations (Relations | Unset):
        tutorial (ConfigTutorial | Unset): Configuration for frontend tutorial (darkened area with highlighted element)
    """

    supported_languages: list[str] | Unset = UNSET
    extension: str | Unset = UNSET
    login_url: str | Unset = UNSET
    login_allow_local: bool | Unset = UNSET
    login_providers_url: str | Unset = UNSET
    login_provider_target_url: str | Unset = UNSET
    login_silent_mode: ValuesLoginSilentMode | Unset = UNSET
    register: Register | Unset = UNSET
    recover_password_url: str | Unset = UNSET
    imprint_url: str | Unset = UNSET
    privacy_information_url: str | Unset = UNSET
    help_url: str | Unset = UNSET
    whats_new_url: str | Unset = UNSET
    edit_profile_url: str | Unset = UNSET
    access_denied_info_url: str | Unset = UNSET
    edit_profile: bool | Unset = UNSET
    workspace_columns: list[str] | Unset = UNSET
    workspace_shared_to_me_default_all: bool | Unset = UNSET
    hide_main_menu: list[str] | Unset = UNSET
    logout: LogoutInfo | Unset = UNSET
    menu_entries: list[MenuEntry] | Unset = UNSET
    custom_options: list[ContextMenuEntry] | Unset = UNSET
    user_menu_overrides: list[ContextMenuEntry] | Unset = UNSET
    allowed_licenses: list[str] | Unset = UNSET
    custom_licenses: list[License] | Unset = UNSET
    workflow: ConfigWorkflow | Unset = UNSET
    license_dialog_on_upload: bool | Unset = UNSET
    node_report: bool | Unset = UNSET
    branding: bool | Unset = UNSET
    rating: ConfigRating | Unset = UNSET
    publishing_notice: bool | Unset = UNSET
    publishing: PublishingConfig | Unset = UNSET
    site_title: str | Unset = UNSET
    user_display_name: str | Unset = UNSET
    user_secondary_display_name: str | Unset = UNSET
    user_affiliation: bool | Unset = UNSET
    default_username: str | Unset = UNSET
    default_password: str | Unset = UNSET
    banner: Banner | Unset = UNSET
    available_mds: list[AvailableMds] | Unset = UNSET
    available_repositories: list[str] | Unset = UNSET
    search_view_type: int | Unset = UNSET
    workspace_view_type: int | Unset = UNSET
    items_per_request: int | Unset = UNSET
    rendering: Rendering | Unset = UNSET
    session_expired_dialog: SessionExpiredDialog | Unset = UNSET
    default_location: str | Unset = UNSET
    login_default_location: str | Unset = UNSET
    search_group_results: bool | Unset = UNSET
    mainnav: Mainnav | Unset = UNSET
    search_sidenav_mode: str | Unset = UNSET
    search_preview_mode: ValuesSearchPreviewMode | Unset = UNSET
    search_filter_bar_width: int | Unset = UNSET
    collections: Collections | Unset = UNSET
    license_agreement: LicenseAgreement | Unset = UNSET
    services: Services | Unset = UNSET
    help_menu_options: list[HelpMenuOptions] | Unset = UNSET
    favicon: str | Unset = UNSET
    apple_touch_icon: str | Unset = UNSET
    images: list[Image] | Unset = UNSET
    icons: list[FontIcon] | Unset = UNSET
    stream: Stream | Unset = UNSET
    admin: Admin | Unset = UNSET
    simple_edit: SimpleEdit | Unset = UNSET
    frontpage: ConfigFrontpage | Unset = UNSET
    upload: ConfigUpload | Unset = UNSET
    publish: ConfigPublish | Unset = UNSET
    remote: ConfigRemote | Unset = UNSET
    report_problem: ConfigReportProblem | Unset = UNSET
    custom_css: str | Unset = UNSET
    theme_colors: list[ConfigThemeColors] | Unset = UNSET
    privacy: ConfigPrivacy | Unset = UNSET
    gdpr: Gdpr | Unset = UNSET
    relations: Relations | Unset = UNSET
    tutorial: ConfigTutorial | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        supported_languages: list[str] | Unset = UNSET
        if not isinstance(self.supported_languages, Unset):
            supported_languages = self.supported_languages

        extension = self.extension

        login_url = self.login_url

        login_allow_local = self.login_allow_local

        login_providers_url = self.login_providers_url

        login_provider_target_url = self.login_provider_target_url

        login_silent_mode: str | Unset = UNSET
        if not isinstance(self.login_silent_mode, Unset):
            login_silent_mode = self.login_silent_mode.value

        register: dict[str, Any] | Unset = UNSET
        if not isinstance(self.register, Unset):
            register = self.register.to_dict()

        recover_password_url = self.recover_password_url

        imprint_url = self.imprint_url

        privacy_information_url = self.privacy_information_url

        help_url = self.help_url

        whats_new_url = self.whats_new_url

        edit_profile_url = self.edit_profile_url

        access_denied_info_url = self.access_denied_info_url

        edit_profile = self.edit_profile

        workspace_columns: list[str] | Unset = UNSET
        if not isinstance(self.workspace_columns, Unset):
            workspace_columns = self.workspace_columns

        workspace_shared_to_me_default_all = self.workspace_shared_to_me_default_all

        hide_main_menu: list[str] | Unset = UNSET
        if not isinstance(self.hide_main_menu, Unset):
            hide_main_menu = self.hide_main_menu

        logout: dict[str, Any] | Unset = UNSET
        if not isinstance(self.logout, Unset):
            logout = self.logout.to_dict()

        menu_entries: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.menu_entries, Unset):
            menu_entries = []
            for menu_entries_item_data in self.menu_entries:
                menu_entries_item = menu_entries_item_data.to_dict()
                menu_entries.append(menu_entries_item)

        custom_options: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.custom_options, Unset):
            custom_options = []
            for custom_options_item_data in self.custom_options:
                custom_options_item = custom_options_item_data.to_dict()
                custom_options.append(custom_options_item)

        user_menu_overrides: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.user_menu_overrides, Unset):
            user_menu_overrides = []
            for user_menu_overrides_item_data in self.user_menu_overrides:
                user_menu_overrides_item = user_menu_overrides_item_data.to_dict()
                user_menu_overrides.append(user_menu_overrides_item)

        allowed_licenses: list[str] | Unset = UNSET
        if not isinstance(self.allowed_licenses, Unset):
            allowed_licenses = self.allowed_licenses

        custom_licenses: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.custom_licenses, Unset):
            custom_licenses = []
            for custom_licenses_item_data in self.custom_licenses:
                custom_licenses_item = custom_licenses_item_data.to_dict()
                custom_licenses.append(custom_licenses_item)

        workflow: dict[str, Any] | Unset = UNSET
        if not isinstance(self.workflow, Unset):
            workflow = self.workflow.to_dict()

        license_dialog_on_upload = self.license_dialog_on_upload

        node_report = self.node_report

        branding = self.branding

        rating: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rating, Unset):
            rating = self.rating.to_dict()

        publishing_notice = self.publishing_notice

        publishing: dict[str, Any] | Unset = UNSET
        if not isinstance(self.publishing, Unset):
            publishing = self.publishing.to_dict()

        site_title = self.site_title

        user_display_name = self.user_display_name

        user_secondary_display_name = self.user_secondary_display_name

        user_affiliation = self.user_affiliation

        default_username = self.default_username

        default_password = self.default_password

        banner: dict[str, Any] | Unset = UNSET
        if not isinstance(self.banner, Unset):
            banner = self.banner.to_dict()

        available_mds: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.available_mds, Unset):
            available_mds = []
            for available_mds_item_data in self.available_mds:
                available_mds_item = available_mds_item_data.to_dict()
                available_mds.append(available_mds_item)

        available_repositories: list[str] | Unset = UNSET
        if not isinstance(self.available_repositories, Unset):
            available_repositories = self.available_repositories

        search_view_type = self.search_view_type

        workspace_view_type = self.workspace_view_type

        items_per_request = self.items_per_request

        rendering: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rendering, Unset):
            rendering = self.rendering.to_dict()

        session_expired_dialog: dict[str, Any] | Unset = UNSET
        if not isinstance(self.session_expired_dialog, Unset):
            session_expired_dialog = self.session_expired_dialog.to_dict()

        default_location = self.default_location

        login_default_location = self.login_default_location

        search_group_results = self.search_group_results

        mainnav: dict[str, Any] | Unset = UNSET
        if not isinstance(self.mainnav, Unset):
            mainnav = self.mainnav.to_dict()

        search_sidenav_mode = self.search_sidenav_mode

        search_preview_mode: str | Unset = UNSET
        if not isinstance(self.search_preview_mode, Unset):
            search_preview_mode = self.search_preview_mode.value

        search_filter_bar_width = self.search_filter_bar_width

        collections: dict[str, Any] | Unset = UNSET
        if not isinstance(self.collections, Unset):
            collections = self.collections.to_dict()

        license_agreement: dict[str, Any] | Unset = UNSET
        if not isinstance(self.license_agreement, Unset):
            license_agreement = self.license_agreement.to_dict()

        services: dict[str, Any] | Unset = UNSET
        if not isinstance(self.services, Unset):
            services = self.services.to_dict()

        help_menu_options: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.help_menu_options, Unset):
            help_menu_options = []
            for help_menu_options_item_data in self.help_menu_options:
                help_menu_options_item = help_menu_options_item_data.to_dict()
                help_menu_options.append(help_menu_options_item)

        favicon = self.favicon

        apple_touch_icon = self.apple_touch_icon

        images: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.images, Unset):
            images = []
            for images_item_data in self.images:
                images_item = images_item_data.to_dict()
                images.append(images_item)

        icons: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.icons, Unset):
            icons = []
            for icons_item_data in self.icons:
                icons_item = icons_item_data.to_dict()
                icons.append(icons_item)

        stream: dict[str, Any] | Unset = UNSET
        if not isinstance(self.stream, Unset):
            stream = self.stream.to_dict()

        admin: dict[str, Any] | Unset = UNSET
        if not isinstance(self.admin, Unset):
            admin = self.admin.to_dict()

        simple_edit: dict[str, Any] | Unset = UNSET
        if not isinstance(self.simple_edit, Unset):
            simple_edit = self.simple_edit.to_dict()

        frontpage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.frontpage, Unset):
            frontpage = self.frontpage.to_dict()

        upload: dict[str, Any] | Unset = UNSET
        if not isinstance(self.upload, Unset):
            upload = self.upload.to_dict()

        publish: dict[str, Any] | Unset = UNSET
        if not isinstance(self.publish, Unset):
            publish = self.publish.to_dict()

        remote: dict[str, Any] | Unset = UNSET
        if not isinstance(self.remote, Unset):
            remote = self.remote.to_dict()

        report_problem: dict[str, Any] | Unset = UNSET
        if not isinstance(self.report_problem, Unset):
            report_problem = self.report_problem.to_dict()

        custom_css = self.custom_css

        theme_colors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.theme_colors, Unset):
            theme_colors = []
            for theme_colors_item_data in self.theme_colors:
                theme_colors_item = theme_colors_item_data.to_dict()
                theme_colors.append(theme_colors_item)

        privacy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.privacy, Unset):
            privacy = self.privacy.to_dict()

        gdpr: dict[str, Any] | Unset = UNSET
        if not isinstance(self.gdpr, Unset):
            gdpr = self.gdpr.to_dict()

        relations: dict[str, Any] | Unset = UNSET
        if not isinstance(self.relations, Unset):
            relations = self.relations.to_dict()

        tutorial: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tutorial, Unset):
            tutorial = self.tutorial.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if supported_languages is not UNSET:
            field_dict["supportedLanguages"] = supported_languages
        if extension is not UNSET:
            field_dict["extension"] = extension
        if login_url is not UNSET:
            field_dict["loginUrl"] = login_url
        if login_allow_local is not UNSET:
            field_dict["loginAllowLocal"] = login_allow_local
        if login_providers_url is not UNSET:
            field_dict["loginProvidersUrl"] = login_providers_url
        if login_provider_target_url is not UNSET:
            field_dict["loginProviderTargetUrl"] = login_provider_target_url
        if login_silent_mode is not UNSET:
            field_dict["loginSilentMode"] = login_silent_mode
        if register is not UNSET:
            field_dict["register"] = register
        if recover_password_url is not UNSET:
            field_dict["recoverPasswordUrl"] = recover_password_url
        if imprint_url is not UNSET:
            field_dict["imprintUrl"] = imprint_url
        if privacy_information_url is not UNSET:
            field_dict["privacyInformationUrl"] = privacy_information_url
        if help_url is not UNSET:
            field_dict["helpUrl"] = help_url
        if whats_new_url is not UNSET:
            field_dict["whatsNewUrl"] = whats_new_url
        if edit_profile_url is not UNSET:
            field_dict["editProfileUrl"] = edit_profile_url
        if access_denied_info_url is not UNSET:
            field_dict["accessDeniedInfoUrl"] = access_denied_info_url
        if edit_profile is not UNSET:
            field_dict["editProfile"] = edit_profile
        if workspace_columns is not UNSET:
            field_dict["workspaceColumns"] = workspace_columns
        if workspace_shared_to_me_default_all is not UNSET:
            field_dict["workspaceSharedToMeDefaultAll"] = workspace_shared_to_me_default_all
        if hide_main_menu is not UNSET:
            field_dict["hideMainMenu"] = hide_main_menu
        if logout is not UNSET:
            field_dict["logout"] = logout
        if menu_entries is not UNSET:
            field_dict["menuEntries"] = menu_entries
        if custom_options is not UNSET:
            field_dict["customOptions"] = custom_options
        if user_menu_overrides is not UNSET:
            field_dict["userMenuOverrides"] = user_menu_overrides
        if allowed_licenses is not UNSET:
            field_dict["allowedLicenses"] = allowed_licenses
        if custom_licenses is not UNSET:
            field_dict["customLicenses"] = custom_licenses
        if workflow is not UNSET:
            field_dict["workflow"] = workflow
        if license_dialog_on_upload is not UNSET:
            field_dict["licenseDialogOnUpload"] = license_dialog_on_upload
        if node_report is not UNSET:
            field_dict["nodeReport"] = node_report
        if branding is not UNSET:
            field_dict["branding"] = branding
        if rating is not UNSET:
            field_dict["rating"] = rating
        if publishing_notice is not UNSET:
            field_dict["publishingNotice"] = publishing_notice
        if publishing is not UNSET:
            field_dict["publishing"] = publishing
        if site_title is not UNSET:
            field_dict["siteTitle"] = site_title
        if user_display_name is not UNSET:
            field_dict["userDisplayName"] = user_display_name
        if user_secondary_display_name is not UNSET:
            field_dict["userSecondaryDisplayName"] = user_secondary_display_name
        if user_affiliation is not UNSET:
            field_dict["userAffiliation"] = user_affiliation
        if default_username is not UNSET:
            field_dict["defaultUsername"] = default_username
        if default_password is not UNSET:
            field_dict["defaultPassword"] = default_password
        if banner is not UNSET:
            field_dict["banner"] = banner
        if available_mds is not UNSET:
            field_dict["availableMds"] = available_mds
        if available_repositories is not UNSET:
            field_dict["availableRepositories"] = available_repositories
        if search_view_type is not UNSET:
            field_dict["searchViewType"] = search_view_type
        if workspace_view_type is not UNSET:
            field_dict["workspaceViewType"] = workspace_view_type
        if items_per_request is not UNSET:
            field_dict["itemsPerRequest"] = items_per_request
        if rendering is not UNSET:
            field_dict["rendering"] = rendering
        if session_expired_dialog is not UNSET:
            field_dict["sessionExpiredDialog"] = session_expired_dialog
        if default_location is not UNSET:
            field_dict["defaultLocation"] = default_location
        if login_default_location is not UNSET:
            field_dict["loginDefaultLocation"] = login_default_location
        if search_group_results is not UNSET:
            field_dict["searchGroupResults"] = search_group_results
        if mainnav is not UNSET:
            field_dict["mainnav"] = mainnav
        if search_sidenav_mode is not UNSET:
            field_dict["searchSidenavMode"] = search_sidenav_mode
        if search_preview_mode is not UNSET:
            field_dict["searchPreviewMode"] = search_preview_mode
        if search_filter_bar_width is not UNSET:
            field_dict["searchFilterBarWidth"] = search_filter_bar_width
        if collections is not UNSET:
            field_dict["collections"] = collections
        if license_agreement is not UNSET:
            field_dict["licenseAgreement"] = license_agreement
        if services is not UNSET:
            field_dict["services"] = services
        if help_menu_options is not UNSET:
            field_dict["helpMenuOptions"] = help_menu_options
        if favicon is not UNSET:
            field_dict["favicon"] = favicon
        if apple_touch_icon is not UNSET:
            field_dict["appleTouchIcon"] = apple_touch_icon
        if images is not UNSET:
            field_dict["images"] = images
        if icons is not UNSET:
            field_dict["icons"] = icons
        if stream is not UNSET:
            field_dict["stream"] = stream
        if admin is not UNSET:
            field_dict["admin"] = admin
        if simple_edit is not UNSET:
            field_dict["simpleEdit"] = simple_edit
        if frontpage is not UNSET:
            field_dict["frontpage"] = frontpage
        if upload is not UNSET:
            field_dict["upload"] = upload
        if publish is not UNSET:
            field_dict["publish"] = publish
        if remote is not UNSET:
            field_dict["remote"] = remote
        if report_problem is not UNSET:
            field_dict["reportProblem"] = report_problem
        if custom_css is not UNSET:
            field_dict["customCSS"] = custom_css
        if theme_colors is not UNSET:
            field_dict["themeColors"] = theme_colors
        if privacy is not UNSET:
            field_dict["privacy"] = privacy
        if gdpr is not UNSET:
            field_dict["gdpr"] = gdpr
        if relations is not UNSET:
            field_dict["relations"] = relations
        if tutorial is not UNSET:
            field_dict["tutorial"] = tutorial

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.admin import Admin
        from ..models.available_mds import AvailableMds
        from ..models.banner import Banner
        from ..models.collections import Collections
        from ..models.config_frontpage import ConfigFrontpage
        from ..models.config_privacy import ConfigPrivacy
        from ..models.config_publish import ConfigPublish
        from ..models.config_rating import ConfigRating
        from ..models.config_remote import ConfigRemote
        from ..models.config_report_problem import ConfigReportProblem
        from ..models.config_theme_colors import ConfigThemeColors
        from ..models.config_tutorial import ConfigTutorial
        from ..models.config_upload import ConfigUpload
        from ..models.config_workflow import ConfigWorkflow
        from ..models.context_menu_entry import ContextMenuEntry
        from ..models.font_icon import FontIcon
        from ..models.gdpr import Gdpr
        from ..models.help_menu_options import HelpMenuOptions
        from ..models.image import Image
        from ..models.license_ import License
        from ..models.license_agreement import LicenseAgreement
        from ..models.logout_info import LogoutInfo
        from ..models.mainnav import Mainnav
        from ..models.menu_entry import MenuEntry
        from ..models.publishing_config import PublishingConfig
        from ..models.register import Register
        from ..models.relations import Relations
        from ..models.rendering import Rendering
        from ..models.services import Services
        from ..models.session_expired_dialog import SessionExpiredDialog
        from ..models.simple_edit import SimpleEdit
        from ..models.stream import Stream

        d = dict(src_dict)
        supported_languages = cast(list[str], d.pop("supportedLanguages", UNSET))

        extension = d.pop("extension", UNSET)

        login_url = d.pop("loginUrl", UNSET)

        login_allow_local = d.pop("loginAllowLocal", UNSET)

        login_providers_url = d.pop("loginProvidersUrl", UNSET)

        login_provider_target_url = d.pop("loginProviderTargetUrl", UNSET)

        _login_silent_mode = d.pop("loginSilentMode", UNSET)
        login_silent_mode: ValuesLoginSilentMode | Unset
        if isinstance(_login_silent_mode, Unset):
            login_silent_mode = UNSET
        else:
            login_silent_mode = ValuesLoginSilentMode(_login_silent_mode)

        _register = d.pop("register", UNSET)
        register: Register | Unset
        if isinstance(_register, Unset):
            register = UNSET
        else:
            register = Register.from_dict(_register)

        recover_password_url = d.pop("recoverPasswordUrl", UNSET)

        imprint_url = d.pop("imprintUrl", UNSET)

        privacy_information_url = d.pop("privacyInformationUrl", UNSET)

        help_url = d.pop("helpUrl", UNSET)

        whats_new_url = d.pop("whatsNewUrl", UNSET)

        edit_profile_url = d.pop("editProfileUrl", UNSET)

        access_denied_info_url = d.pop("accessDeniedInfoUrl", UNSET)

        edit_profile = d.pop("editProfile", UNSET)

        workspace_columns = cast(list[str], d.pop("workspaceColumns", UNSET))

        workspace_shared_to_me_default_all = d.pop("workspaceSharedToMeDefaultAll", UNSET)

        hide_main_menu = cast(list[str], d.pop("hideMainMenu", UNSET))

        _logout = d.pop("logout", UNSET)
        logout: LogoutInfo | Unset
        if isinstance(_logout, Unset):
            logout = UNSET
        else:
            logout = LogoutInfo.from_dict(_logout)

        _menu_entries = d.pop("menuEntries", UNSET)
        menu_entries: list[MenuEntry] | Unset = UNSET
        if _menu_entries is not UNSET:
            menu_entries = []
            for menu_entries_item_data in _menu_entries:
                menu_entries_item = MenuEntry.from_dict(menu_entries_item_data)

                menu_entries.append(menu_entries_item)

        _custom_options = d.pop("customOptions", UNSET)
        custom_options: list[ContextMenuEntry] | Unset = UNSET
        if _custom_options is not UNSET:
            custom_options = []
            for custom_options_item_data in _custom_options:
                custom_options_item = ContextMenuEntry.from_dict(custom_options_item_data)

                custom_options.append(custom_options_item)

        _user_menu_overrides = d.pop("userMenuOverrides", UNSET)
        user_menu_overrides: list[ContextMenuEntry] | Unset = UNSET
        if _user_menu_overrides is not UNSET:
            user_menu_overrides = []
            for user_menu_overrides_item_data in _user_menu_overrides:
                user_menu_overrides_item = ContextMenuEntry.from_dict(user_menu_overrides_item_data)

                user_menu_overrides.append(user_menu_overrides_item)

        allowed_licenses = cast(list[str], d.pop("allowedLicenses", UNSET))

        _custom_licenses = d.pop("customLicenses", UNSET)
        custom_licenses: list[License] | Unset = UNSET
        if _custom_licenses is not UNSET:
            custom_licenses = []
            for custom_licenses_item_data in _custom_licenses:
                custom_licenses_item = License.from_dict(custom_licenses_item_data)

                custom_licenses.append(custom_licenses_item)

        _workflow = d.pop("workflow", UNSET)
        workflow: ConfigWorkflow | Unset
        if isinstance(_workflow, Unset):
            workflow = UNSET
        else:
            workflow = ConfigWorkflow.from_dict(_workflow)

        license_dialog_on_upload = d.pop("licenseDialogOnUpload", UNSET)

        node_report = d.pop("nodeReport", UNSET)

        branding = d.pop("branding", UNSET)

        _rating = d.pop("rating", UNSET)
        rating: ConfigRating | Unset
        if isinstance(_rating, Unset):
            rating = UNSET
        else:
            rating = ConfigRating.from_dict(_rating)

        publishing_notice = d.pop("publishingNotice", UNSET)

        _publishing = d.pop("publishing", UNSET)
        publishing: PublishingConfig | Unset
        if isinstance(_publishing, Unset):
            publishing = UNSET
        else:
            publishing = PublishingConfig.from_dict(_publishing)

        site_title = d.pop("siteTitle", UNSET)

        user_display_name = d.pop("userDisplayName", UNSET)

        user_secondary_display_name = d.pop("userSecondaryDisplayName", UNSET)

        user_affiliation = d.pop("userAffiliation", UNSET)

        default_username = d.pop("defaultUsername", UNSET)

        default_password = d.pop("defaultPassword", UNSET)

        _banner = d.pop("banner", UNSET)
        banner: Banner | Unset
        if isinstance(_banner, Unset):
            banner = UNSET
        else:
            banner = Banner.from_dict(_banner)

        _available_mds = d.pop("availableMds", UNSET)
        available_mds: list[AvailableMds] | Unset = UNSET
        if _available_mds is not UNSET:
            available_mds = []
            for available_mds_item_data in _available_mds:
                available_mds_item = AvailableMds.from_dict(available_mds_item_data)

                available_mds.append(available_mds_item)

        available_repositories = cast(list[str], d.pop("availableRepositories", UNSET))

        search_view_type = d.pop("searchViewType", UNSET)

        workspace_view_type = d.pop("workspaceViewType", UNSET)

        items_per_request = d.pop("itemsPerRequest", UNSET)

        _rendering = d.pop("rendering", UNSET)
        rendering: Rendering | Unset
        if isinstance(_rendering, Unset):
            rendering = UNSET
        else:
            rendering = Rendering.from_dict(_rendering)

        _session_expired_dialog = d.pop("sessionExpiredDialog", UNSET)
        session_expired_dialog: SessionExpiredDialog | Unset
        if isinstance(_session_expired_dialog, Unset):
            session_expired_dialog = UNSET
        else:
            session_expired_dialog = SessionExpiredDialog.from_dict(_session_expired_dialog)

        default_location = d.pop("defaultLocation", UNSET)

        login_default_location = d.pop("loginDefaultLocation", UNSET)

        search_group_results = d.pop("searchGroupResults", UNSET)

        _mainnav = d.pop("mainnav", UNSET)
        mainnav: Mainnav | Unset
        if isinstance(_mainnav, Unset):
            mainnav = UNSET
        else:
            mainnav = Mainnav.from_dict(_mainnav)

        search_sidenav_mode = d.pop("searchSidenavMode", UNSET)

        _search_preview_mode = d.pop("searchPreviewMode", UNSET)
        search_preview_mode: ValuesSearchPreviewMode | Unset
        if isinstance(_search_preview_mode, Unset):
            search_preview_mode = UNSET
        else:
            search_preview_mode = ValuesSearchPreviewMode(_search_preview_mode)

        search_filter_bar_width = d.pop("searchFilterBarWidth", UNSET)

        _collections = d.pop("collections", UNSET)
        collections: Collections | Unset
        if isinstance(_collections, Unset):
            collections = UNSET
        else:
            collections = Collections.from_dict(_collections)

        _license_agreement = d.pop("licenseAgreement", UNSET)
        license_agreement: LicenseAgreement | Unset
        if isinstance(_license_agreement, Unset):
            license_agreement = UNSET
        else:
            license_agreement = LicenseAgreement.from_dict(_license_agreement)

        _services = d.pop("services", UNSET)
        services: Services | Unset
        if isinstance(_services, Unset):
            services = UNSET
        else:
            services = Services.from_dict(_services)

        _help_menu_options = d.pop("helpMenuOptions", UNSET)
        help_menu_options: list[HelpMenuOptions] | Unset = UNSET
        if _help_menu_options is not UNSET:
            help_menu_options = []
            for help_menu_options_item_data in _help_menu_options:
                help_menu_options_item = HelpMenuOptions.from_dict(help_menu_options_item_data)

                help_menu_options.append(help_menu_options_item)

        favicon = d.pop("favicon", UNSET)

        apple_touch_icon = d.pop("appleTouchIcon", UNSET)

        _images = d.pop("images", UNSET)
        images: list[Image] | Unset = UNSET
        if _images is not UNSET:
            images = []
            for images_item_data in _images:
                images_item = Image.from_dict(images_item_data)

                images.append(images_item)

        _icons = d.pop("icons", UNSET)
        icons: list[FontIcon] | Unset = UNSET
        if _icons is not UNSET:
            icons = []
            for icons_item_data in _icons:
                icons_item = FontIcon.from_dict(icons_item_data)

                icons.append(icons_item)

        _stream = d.pop("stream", UNSET)
        stream: Stream | Unset
        if isinstance(_stream, Unset):
            stream = UNSET
        else:
            stream = Stream.from_dict(_stream)

        _admin = d.pop("admin", UNSET)
        admin: Admin | Unset
        if isinstance(_admin, Unset):
            admin = UNSET
        else:
            admin = Admin.from_dict(_admin)

        _simple_edit = d.pop("simpleEdit", UNSET)
        simple_edit: SimpleEdit | Unset
        if isinstance(_simple_edit, Unset):
            simple_edit = UNSET
        else:
            simple_edit = SimpleEdit.from_dict(_simple_edit)

        _frontpage = d.pop("frontpage", UNSET)
        frontpage: ConfigFrontpage | Unset
        if isinstance(_frontpage, Unset):
            frontpage = UNSET
        else:
            frontpage = ConfigFrontpage.from_dict(_frontpage)

        _upload = d.pop("upload", UNSET)
        upload: ConfigUpload | Unset
        if isinstance(_upload, Unset):
            upload = UNSET
        else:
            upload = ConfigUpload.from_dict(_upload)

        _publish = d.pop("publish", UNSET)
        publish: ConfigPublish | Unset
        if isinstance(_publish, Unset):
            publish = UNSET
        else:
            publish = ConfigPublish.from_dict(_publish)

        _remote = d.pop("remote", UNSET)
        remote: ConfigRemote | Unset
        if isinstance(_remote, Unset):
            remote = UNSET
        else:
            remote = ConfigRemote.from_dict(_remote)

        _report_problem = d.pop("reportProblem", UNSET)
        report_problem: ConfigReportProblem | Unset
        if isinstance(_report_problem, Unset):
            report_problem = UNSET
        else:
            report_problem = ConfigReportProblem.from_dict(_report_problem)

        custom_css = d.pop("customCSS", UNSET)

        _theme_colors = d.pop("themeColors", UNSET)
        theme_colors: list[ConfigThemeColors] | Unset = UNSET
        if _theme_colors is not UNSET:
            theme_colors = []
            for theme_colors_item_data in _theme_colors:
                theme_colors_item = ConfigThemeColors.from_dict(theme_colors_item_data)

                theme_colors.append(theme_colors_item)

        _privacy = d.pop("privacy", UNSET)
        privacy: ConfigPrivacy | Unset
        if isinstance(_privacy, Unset):
            privacy = UNSET
        else:
            privacy = ConfigPrivacy.from_dict(_privacy)

        _gdpr = d.pop("gdpr", UNSET)
        gdpr: Gdpr | Unset
        if isinstance(_gdpr, Unset):
            gdpr = UNSET
        else:
            gdpr = Gdpr.from_dict(_gdpr)

        _relations = d.pop("relations", UNSET)
        relations: Relations | Unset
        if isinstance(_relations, Unset):
            relations = UNSET
        else:
            relations = Relations.from_dict(_relations)

        _tutorial = d.pop("tutorial", UNSET)
        tutorial: ConfigTutorial | Unset
        if isinstance(_tutorial, Unset):
            tutorial = UNSET
        else:
            tutorial = ConfigTutorial.from_dict(_tutorial)

        values = cls(
            supported_languages=supported_languages,
            extension=extension,
            login_url=login_url,
            login_allow_local=login_allow_local,
            login_providers_url=login_providers_url,
            login_provider_target_url=login_provider_target_url,
            login_silent_mode=login_silent_mode,
            register=register,
            recover_password_url=recover_password_url,
            imprint_url=imprint_url,
            privacy_information_url=privacy_information_url,
            help_url=help_url,
            whats_new_url=whats_new_url,
            edit_profile_url=edit_profile_url,
            access_denied_info_url=access_denied_info_url,
            edit_profile=edit_profile,
            workspace_columns=workspace_columns,
            workspace_shared_to_me_default_all=workspace_shared_to_me_default_all,
            hide_main_menu=hide_main_menu,
            logout=logout,
            menu_entries=menu_entries,
            custom_options=custom_options,
            user_menu_overrides=user_menu_overrides,
            allowed_licenses=allowed_licenses,
            custom_licenses=custom_licenses,
            workflow=workflow,
            license_dialog_on_upload=license_dialog_on_upload,
            node_report=node_report,
            branding=branding,
            rating=rating,
            publishing_notice=publishing_notice,
            publishing=publishing,
            site_title=site_title,
            user_display_name=user_display_name,
            user_secondary_display_name=user_secondary_display_name,
            user_affiliation=user_affiliation,
            default_username=default_username,
            default_password=default_password,
            banner=banner,
            available_mds=available_mds,
            available_repositories=available_repositories,
            search_view_type=search_view_type,
            workspace_view_type=workspace_view_type,
            items_per_request=items_per_request,
            rendering=rendering,
            session_expired_dialog=session_expired_dialog,
            default_location=default_location,
            login_default_location=login_default_location,
            search_group_results=search_group_results,
            mainnav=mainnav,
            search_sidenav_mode=search_sidenav_mode,
            search_preview_mode=search_preview_mode,
            search_filter_bar_width=search_filter_bar_width,
            collections=collections,
            license_agreement=license_agreement,
            services=services,
            help_menu_options=help_menu_options,
            favicon=favicon,
            apple_touch_icon=apple_touch_icon,
            images=images,
            icons=icons,
            stream=stream,
            admin=admin,
            simple_edit=simple_edit,
            frontpage=frontpage,
            upload=upload,
            publish=publish,
            remote=remote,
            report_problem=report_problem,
            custom_css=custom_css,
            theme_colors=theme_colors,
            privacy=privacy,
            gdpr=gdpr,
            relations=relations,
            tutorial=tutorial,
        )

        values.additional_properties = d
        return values

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
