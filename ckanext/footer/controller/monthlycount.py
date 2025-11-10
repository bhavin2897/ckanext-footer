# controller/monthlycount.py
import datetime
import logging
from ckan.plugins import toolkit as t

log = logging.getLogger(__name__)


class MonthlyCountController:
    # will be overwritten from plugin.configure
    DATASET_NAME = 'site-monthly-counts'
    RESOURCE_NAME = 'monthly_counts'
    OWNER_ORG = '0170ebc4-b55a-47a9-96b2-9981cef2ac7e'
    OWNER_TYPE = 'repository'

    @staticmethod
    def _owner_org_id(context, owner_org):
        log.debug('_owner_org_id: input=%s', owner_org)
        try:
            org = t.get_action('organization_show')(context, {'id': owner_org})
            log.debug('_owner_org_id: resolved id=%s name=%s', org.get('id'), org.get('name'))
            return org['id']
        except Exception as e:
            log.debug('_owner_org_id: fallback to input, reason=%s', e)
            return owner_org

    @staticmethod
    def _ensure_private_metrics_resource(context):
        pkg_show = t.get_action('package_show')
        pkg_create = t.get_action('package_create')
        pkg_update = t.get_action('package_update')
        res_create = t.get_action('resource_create')
        res_update = t.get_action('resource_update')

        dataset_name = MonthlyCountController.DATASET_NAME
        resource_name = MonthlyCountController.RESOURCE_NAME
        owner_org = MonthlyCountController.OWNER_ORG
        log.debug('_ensure_private_metrics_resource: dataset=%s resource=%s owner_org=%s',
                  dataset_name, resource_name, owner_org)

        # get or create package
        try:
            pkg = pkg_show(context, {'id': dataset_name})
            log.debug('_ensure_private_metrics_resource: package exists id=%s state=%s',
                      pkg.get('id'), pkg.get('state'))
        except t.ObjectNotFound:
            log.debug('_ensure_private_metrics_resource: package missing, creating')
            try:
                pkg = pkg_create(context, {
                    'name': dataset_name,
                    'title': 'Site Monthly Counts (Admin Only)',
                    'private': True,
                    'owner_org': MonthlyCountController._owner_org_id(context, owner_org),
                    'notes': 'Monthly snapshots of totals and per-organization dataset counts.'
                })
                log.debug('_ensure_private_metrics_resource: package created id=%s', pkg.get('id'))
            except t.ValidationError as e:
                log.debug('_ensure_private_metrics_resource: package_create ValidationError=%s', e.error_dict)
                pkg = pkg_show({'ignore_auth': True}, {'id': dataset_name})
                log.debug('_ensure_private_metrics_resource: fetched existing package id=%s', pkg.get('id'))

        if pkg.get('state') == 'deleted':
            log.debug('_ensure_private_metrics_resource: undeleting package id=%s', pkg.get('id'))
            pkg = pkg_update(context, {'id': pkg['id'], 'state': 'active'})

        # find resource by name
        for r in pkg.get('resources', []):
            if r.get('name') == resource_name:
                log.debug('_ensure_private_metrics_resource: found resource id=%s state=%s url_type=%s',
                          r.get('id'), r.get('state'), r.get('url_type'))
                # Ensure it's active and writable by datastore
                if r.get('state') == 'deleted':
                    r = t.get_action('resource_update')(context, {'id': r['id'], 'state': 'active'})
                    log.debug('_ensure_private_metrics_resource: undeleted resource id=%s', r.get('id'))
                if r.get('url_type') != 'datastore':
                    log.debug('_ensure_private_metrics_resource: fixing url_type to datastore')
                    res_update(context, {'id': r['id'], 'url': 'datastore', 'url_type': 'datastore'})
                return r['id']

        # create resource if missing
        log.debug('_ensure_private_metrics_resource: creating resource %s', resource_name)
        r = res_create(context, {
            'package_id': pkg['id'],
            'name': resource_name,
            'format': 'CSV',
            'url': 'datastore',
            'url_type': 'datastore'
        })
        log.debug('_ensure_private_metrics_resource: resource created id=%s', r.get('id'))

        # init datastore schema once
        try:
            log.debug('_ensure_private_metrics_resource: creating datastore schema')
            t.get_action('datastore_create')(context, {
                'resource_id': r['id'],
                'force': True,
                'primary_key': ['snapshot_date', 'org_name'],
                'fields': [
                    {'id': 'snapshot_date', 'type': 'date'},
                    {'id': 'org_name', 'type': 'text'},
                    {'id': 'dataset_count', 'type': 'int'},
                ]
            })
            log.debug('_ensure_private_metrics_resource: datastore schema created')
        except t.ValidationError as e:
            log.debug('_ensure_private_metrics_resource: datastore_create ValidationError (likely exists): %s', e.error_dict)

        return r['id']

    @staticmethod
    def _get_or_bootstrap_resource(context):
        res_id = MonthlyCountController._ensure_private_metrics_resource(context)
        log.debug('_get_or_bootstrap_resource: ensured resource id=%s', res_id)

        # ensure datastore exists (if someone recreated resource without DS)
        try:
            t.get_action('datastore_info')(context, {'resource_id': res_id})
            log.debug('_get_or_bootstrap_resource: datastore_info OK for %s', res_id)
        except t.ValidationError as e:
            log.debug('_get_or_bootstrap_resource: datastore_info failed, creating: %s', e.error_dict)
            t.get_action('datastore_create')(context, {
                'resource_id': res_id,
                'force': True,
                'primary_key': ['snapshot_date', 'org_name'],
                'fields': [
                    {'id': 'snapshot_date', 'type': 'date'},
                    {'id': 'org_name', 'type': 'text'},
                    {'id': 'dataset_count', 'type': 'int'},
                ]
            })
            log.debug('_get_or_bootstrap_resource: datastore created for %s', res_id)

        return res_id

    @staticmethod
    def _count_total(context):
        out = t.get_action('package_search')(context, {'q': '*:*', 'rows': 0})
        count = int(out['count'])
        log.debug('_count_total: count=%d', count)
        return count

    @staticmethod
    def _org_handles(context):
        orgs = t.get_action('organization_list')(context,
        {'type': 'repository', 'sort': 'package_count desc', 'all_fields': True}
    )

        repos = []
        for name in orgs:
            try:
                org = t.get_action('organization_show')(context, data_dict={'id': name['id']})
                if org.get('type') == 'repository':
                    repos.append(org)
                    log.debug("_org_handles: KEEP org=%s type=%s", org.get('name'), org.get('type'))
                else:
                    log.debug("_org_handles: skip org=%s type=%s", org.get('name'), org.get('type'))
            except Exception as e:
                log.debug("_org_handles: failed loading org '%s' error=%s", name, e)

        log.debug('_org_handles: filtered to %d repository orgs', len(repos))
        return repos

    @staticmethod
    def _count_for_org(context, org_id):

        log.debug(f'COUNTING STARTS for {org_id} ')
        out = t.get_action('package_search')(context, {'fq': 'owner_org:{}'.format(org_id), 'rows': 0})
        log.debug("_count_for_org: count=%s for org_id=%s", out['count'], org_id)
        cnt = int(out['count'])
        log.debug('_count_for_org: count=%s for org_id=%s', cnt, org_id)
        return cnt

    @staticmethod
    def _snapshot_now(context, snapshot_date=None):
        """Compute counts and upsert to the Datastore."""
        log.debug('_snapshot_now: start snapshot_date=%s', snapshot_date)
        res_id = MonthlyCountController._ensure_private_metrics_resource(context)
        log.debug('_snapshot_now: target res_id=%s', res_id)

        today = (snapshot_date or datetime.date.today()).isoformat()
        log.debug('_snapshot_now: today=%s', today)

        total = MonthlyCountController._count_total(context)
        records = [{
            'snapshot_date': today,
            'org_name': '__TOTAL__',
            'dataset_count': total
        }]
        log.debug('_snapshot_now: appended TOTAL=%d', total)

        for org in MonthlyCountController._org_handles(context):
            org_id = org['id'] or org['name']
            org_label = org['title'] or org['name']
            log.debug(f'Organization handles sent to count {org_label}:{org_id} ')
            try:
                org_count = MonthlyCountController._count_for_org(context, org_id)
                records.append({
                    'snapshot_date': today,
                    'org_name': org_label,
                    'dataset_count': org_count
                })
                log.debug("_snapshot_now: appended record {'snapshot_date': %s, 'org_name': %s, 'dataset_count': %d}",
                          today, org_label, org_count)
            except Exception as e:
                log.debug('_snapshot_now: skipping org_id=%s error=%s', org_id, e)

        log.debug('_snapshot_now: upserting %d records to datastore', len(records))
        t.get_action('datastore_upsert')(context, {
            'resource_id': res_id,
            'method': 'upsert',
            'force': True,  # critical when resource has read-only flag
            'records': records
        })
        log.info('_snapshot_now: upserted %d records into %s', len(records), res_id)
        return res_id

    @staticmethod
    def _is_sysadmin():
        user = t.c.user
        log.debug('_is_sysadmin: user=%s', user)
        if not user:
            return False
        try:
            is_sa = t.get_action('user_show')({'ignore_auth': True}, {'id': user}).get('sysadmin', False)
            log.debug('_is_sysadmin: %s', is_sa)
            return is_sa
        except Exception as e:
            log.debug('_is_sysadmin: error=%s', e)
            return False
