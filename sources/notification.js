import Gio from 'gi://Gio';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// Shows desktop and application notifications in the Dynamic Island
export class NotificationSource {
    constructor(island, settings) {
        this._island = island;
        this._settings = settings;
        this._sources = new Set();
        this._originalBannerBlocked = Main.messageTray?.bannerBlocked ?? false;

        this._settings.connectObject(
            'changed::show-notifications', () => this._sync(),
            'changed::hide-native-banners', () => this._syncBanners(),
            this
        );

        this._initSourceTracking();
        this._sync();
    }

    _initSourceTracking() {
        if (!Main.messageTray)
            return;

        for (const source of Main.messageTray.getSources())
            this._addSource(source);

        Main.messageTray.connectObject(
            'source-added', (_tray, source) => this._addSource(source),
            'source-removed', (_tray, source) => this._removeSource(source),
            this
        );
    }

    _addSource(source) {
        if (!source || this._sources.has(source))
            return;
        this._sources.add(source);

        source.connectObject(
            'notification-request-banner', (_src, notification) => this._onNotification(source, notification),
            'destroy', () => this._removeSource(source),
            this
        );
    }

    _removeSource(source) {
        if (!this._sources.has(source))
            return;
        this._sources.delete(source);
        source.disconnectObject(this);
    }

    _onNotification(source, notification) {
        if (!this._settings.get_boolean('show-notifications'))
            return;
        if (!notification || notification.acknowledged)
            return;

        const icon = notification.gicon ?? source.icon ?? (source.get_icon ? source.get_icon() : null) ?? 'dialog-information-symbolic';
        const title = notification.title || source.title || 'Notification';
        const body = notification.bannerBodyText || notification.body || '';

        this._island.toast(icon, title, {
            subtitle: body,
            notification,
            duration: 4500,
        });
    }

    _sync() {
        this._syncBanners();
    }

    _syncBanners() {
        if (!Main.messageTray)
            return;

        const hide = this._settings.get_boolean('show-notifications') &&
                     this._settings.get_boolean('hide-native-banners');
        Main.messageTray.bannerBlocked = hide;
    }

    destroy() {
        if (Main.messageTray) {
            Main.messageTray.bannerBlocked = this._originalBannerBlocked;
            Main.messageTray.disconnectObject(this);
        }

        for (const source of this._sources)
            source.disconnectObject(this);
        this._sources.clear();

        this._settings?.disconnectObject(this);
        this._island = null;
        this._settings = null;
    }
}
