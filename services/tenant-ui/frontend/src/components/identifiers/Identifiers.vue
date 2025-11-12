<template>
  <MainCardContent
    :title="$t('identifiers.identifiers')"
    :refresh-callback="refreshWebvh"
  >
    <div v-if="pageLoading" class="flex justify-content-center">
      <ProgressSpinner />
    </div>
    <template v-else>
      <Message
        v-if="needsWebvhConfig"
        severity="warn"
        :closable="false"
        class="config-warning"
      >
        <div class="config-warning-content">
          <p class="mb-2">
            {{ $t('identifiers.webvh.connectEndorserPrompt') }}
            <RouterLink :to="{ name: 'Profile' }" class="config-warning-link">
              {{ $t('identifiers.webvh.connectEndorserLink') }}
            </RouterLink>
          </p>
        </div>
      </Message>
      <DataTable
        v-model:filters="didTableFilters"
        :value="webvhDidRows"
        :paginator="true"
        :rows="TABLE_OPT.ROWS_DEFAULT"
        :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
        :global-filter-fields="['alias', 'namespace', 'did', 'status']"
        data-key="did"
        size="small"
        striped-rows
        sort-field="alias"
        :loading="refreshingWebvh || !webvhConfigLoaded"
        removable-sort
      >
        <template #header>
          <div class="table-header">
            <div class="left">
              <Button
                type="button"
                icon="pi pi-plus"
                :label="$t('identifiers.webvh.createButton')"
                class="p-button"
                :disabled="needsWebvhConfig || !availableWebvhServers.length"
                @click="openCreateDialog"
              />
            </div>
            <IconField icon-position="left" class="search-field">
              <InputIcon><i class="pi pi-search" /></InputIcon>
              <InputText
                v-model="didTableFilters.global.value"
                :placeholder="$t('identifiers.webvh.searchPlaceholder')"
              />
            </IconField>
          </div>
        </template>
        <template #empty>{{ $t('common.noRecordsFound') }}</template>
        <template #loading>{{ $t('common.loading') }}</template>
        <Column
          field="namespace"
          :header="$t('identifiers.webvh.namespace')"
          sortable
        />
        <Column
          field="alias"
          :header="$t('identifiers.webvh.alias')"
          sortable
        />
        <Column
          field="status"
          :header="$t('identifiers.webvh.statusHeader')"
          sortable
        >
          <template #body="{ data }">
            <span :class="['status-chip', data.status]">
              {{ statusLabel(data.status) }}
            </span>
          </template>
        </Column>
        <Column
          field="created"
          :header="$t('identifiers.webvh.createdAt')"
          sortable
        />
        <Column field="did" :header="$t('identifiers.webvh.didHeader')">
          <template #body="{ data }">
            <code>{{ data.did }}</code>
          </template>
        </Column>
      </DataTable>

      <Dialog
        v-model:visible="showCreateDidDialog"
        modal
        :header="$t('identifiers.webvh.createDialogTitle')"
        :style="{ width: '32rem' }"
        @hide="resetCreateForm"
      >
        <div class="dialog-content">
          <div class="field">
            <label for="server-select">
              {{ $t('identifiers.webvh.serverUrl') }}
            </label>
            <Dropdown
              id="server-select"
              v-model="selectedWebvhServer"
              :options="availableWebvhServers"
              option-label="label"
              option-value="value"
              class="w-full"
              :disabled="!availableWebvhServers.length"
            />
            <small v-if="!availableWebvhServers.length" class="p-error">
              {{ $t('identifiers.webvh.serverUrlMissing') }}
            </small>
          </div>
          <div class="field">
            <label for="dialog-alias" class="required-label">
              {{ $t('identifiers.webvh.alias') }}
            </label>
            <InputText
              id="dialog-alias"
              v-model.trim="newDidAlias"
              autocomplete="off"
              :class="{ 'p-invalid': createFormTouched && !newDidAlias }"
            />
            <small v-if="createFormTouched && !newDidAlias" class="p-error">
              {{ $t('identifiers.webvh.aliasRequired') }}
            </small>
          </div>
          <div class="field">
            <label for="dialog-namespace">
              {{ $t('identifiers.webvh.namespace') }}
            </label>
            <InputText
              id="dialog-namespace"
              v-model.trim="newDidNamespace"
              autocomplete="off"
            />
          </div>
        </div>
        <template #footer>
          <Button
            type="button"
            class="p-button-text"
            :disabled="creatingDid"
            :label="$t('common.cancel')"
            @click="closeCreateDialog"
          />
          <Button
            type="button"
            icon="pi pi-plus"
            :disabled="!canCreateDid"
            :loading="creatingDid"
            :label="$t('identifiers.webvh.createButton')"
            @click="submitCreateDid"
          />
        </template>
      </Dialog>
    </template>
  </MainCardContent>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watchEffect } from 'vue';
import { RouterLink } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useToast } from 'vue-toastification';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import { FilterMatchMode } from 'primevue/api';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import { useAcapyApi } from '@/store/acapyApi';
import { useTenantStore } from '@/store';
import type { ServerConfig } from '@/types';

const { t } = useI18n();
const toast = useToast();
const tenantStore = useTenantStore();
const acapyApi = useAcapyApi();
const { tenantWallet, loading, serverConfig } = storeToRefs(tenantStore);
const creatingDid = ref(false);
const refreshingWebvh = ref(false);
const showCreateDidDialog = ref(false);
const createFormTouched = ref(false);
const newDidAlias = ref('');
const newDidNamespace = ref('default');
const selectedWebvhServer = ref<string | null>(null);
const webvhConfigData = ref<any | null>(null);
const webvhConfigLoaded = ref(false);
const didTableFilters = ref({
  global: { value: '', matchMode: FilterMatchMode.CONTAINS },
});

const serverConfigValue = computed<ServerConfig | null>(() => {
  const value = serverConfig.value as ServerConfig | undefined;
  return value && 'config' in value ? value : null;
});

const serverWebvhConfig = computed(() => {
  const pluginConfig = serverConfigValue.value?.config?.plugin_config;
  if (!pluginConfig) {
    return null;
  }
  const keyedConfig = pluginConfig as typeof pluginConfig & Record<string, any>;
  return keyedConfig.webvh ?? keyedConfig['did-webvh'] ?? null;
});

const availableWebvhServers = computed(() => {
  if (!serverWebvhConfig.value?.server_url) {
    return [] as Array<{ label: string; value: string }>;
  }
  let label = serverWebvhConfig.value.server_url;
  try {
    const parsed = new URL(serverWebvhConfig.value.server_url);
    label = parsed.hostname;
  } catch (_error) {
    // leave label as raw server_url
  }
  return [
    {
      label,
      value: serverWebvhConfig.value.server_url,
    },
  ];
});

watchEffect(() => {
  if (!selectedWebvhServer.value && availableWebvhServers.value.length) {
    selectedWebvhServer.value = availableWebvhServers.value[0].value;
  }
});

const pageLoading = computed(() => {
  if (loading.value) {
    return true;
  }
  if (webvhConfigData.value) {
    return false;
  }
  if (webvhConfigLoaded.value) {
    return false;
  }
  if ('config' in (serverConfig.value ?? {})) {
    return false;
  }
  return true;
});

const webvhConfig = computed<any | null>(() => {
  const override = webvhConfigData.value;
  const base = serverWebvhConfig.value;
  if (!override || Object.keys(override).length === 0) {
    return base ?? override ?? null;
  }
  if (!base) {
    return override;
  }
  return {
    ...base,
    ...override,
  };
});

const hasWebvhConfig = computed(() => {
  const cfg = webvhConfig.value;
  if (!cfg) {
    return false;
  }
  const witnesses = cfg.witnesses ?? cfg.watchers;
  const hasWitnesses = Array.isArray(witnesses) && witnesses.length > 0;
  return Boolean(cfg.server_url && hasWitnesses);
});

const needsWebvhConfig = computed(() => !hasWebvhConfig.value);

const webvhDidRows = computed(() => {
  const scids = webvhConfig.value?.scids;
  if (!scids || typeof scids !== 'object') {
    return [] as Array<{
      scid: string;
      did: string;
      alias: string;
      namespace: string;
      status: string;
      created: string;
    }>;
  }
  const entries = Object.entries(scids as Record<string, string>);
  return entries.map(([scid, did]) => {
    const segments = (did as string).split(':');
    const alias = segments[segments.length - 1] ?? did;
    const namespace =
      segments.length > 2 ? segments[segments.length - 2] : 'default';
    return {
      scid,
      did,
      alias,
      namespace,
      status: 'active',
      created: '—',
    };
  });
});

const statusLabel = (_status: string) =>
  t('identifiers.webvh.statusActive') as string;

const canCreateDid = computed(
  () =>
    !needsWebvhConfig.value &&
    selectedWebvhServer.value &&
    newDidAlias.value.trim().length > 0 &&
    !creatingDid.value
);

const openCreateDialog = () => {
  if (needsWebvhConfig.value || !availableWebvhServers.value.length) {
    return;
  }
  createFormTouched.value = false;
  if (!newDidNamespace.value) {
    newDidNamespace.value = 'default';
  }
  showCreateDidDialog.value = true;
};

const closeCreateDialog = () => {
  showCreateDidDialog.value = false;
};

const resetCreateForm = () => {
  newDidAlias.value = '';
  newDidNamespace.value = 'default';
  selectedWebvhServer.value = availableWebvhServers.value.length
    ? availableWebvhServers.value[0].value
    : null;
  createFormTouched.value = false;
};

const submitCreateDid = async () => {
  createFormTouched.value = true;
  if (!newDidAlias.value.trim()) {
    return;
  }
  await createDid();
};

const loadWebvhConfig = async () => {
  webvhConfigLoaded.value = false;
  try {
    const response = await acapyApi.getHttp(API_PATH.DID_WEBVH_CONFIG);
    const configData = response?.data ?? response ?? null;
    const isEmptyConfig =
      !configData ||
      (typeof configData === 'object' && Object.keys(configData).length === 0);
    webvhConfigData.value = isEmptyConfig ? null : configData;
  } catch (_error) {
    webvhConfigData.value = null;
  } finally {
    webvhConfigLoaded.value = true;
  }
};

const refreshWebvh = async () => {
  if (refreshingWebvh.value) {
    return;
  }
  refreshingWebvh.value = true;
  try {
    await tenantStore.getServerConfig();
    await loadWebvhConfig();
  } finally {
    refreshingWebvh.value = false;
  }
};

const createDid = async () => {
  creatingDid.value = true;
  try {
    if (needsWebvhConfig.value || !selectedWebvhServer.value) {
      toast.error(t('identifiers.webvh.serverUrlMissing') as string);
      return;
    }
    const alias = newDidAlias.value.trim();
    const namespace = newDidNamespace.value.trim() || 'default';

    const options: Record<string, any> = {
      identifier: alias,
      namespace,
    };

    const response = await acapyApi.postHttp(API_PATH.DID_WEBVH_CREATE, {
      options,
    });

    const newDid = response?.data?.did ?? response?.data?.did_document?.id;
    toast.success(
      newDid
        ? t('identifiers.webvh.createSuccessWithDid', { did: newDid })
        : t('identifiers.webvh.createSuccess')
    );
    resetCreateForm();
    showCreateDidDialog.value = false;
    await tenantStore.getServerConfig();
    await loadWebvhConfig();
  } catch (error: any) {
    toast.error(
      `Failed to create DID: ${
        error?.response?.data?.message ??
        JSON.stringify(error?.response?.data ?? error)
      }`
    );
  } finally {
    creatingDid.value = false;
  }
};

onMounted(async () => {
  const tasks: Promise<any>[] = [];
  if (!tenantWallet.value) {
    tasks.push(tenantStore.getTenantSubWallet());
  }
  if (!('config' in (serverConfig.value ?? {}))) {
    tasks.push(tenantStore.getServerConfig());
  }
  if (tasks.length) {
    await Promise.allSettled(tasks);
  }
  await loadWebvhConfig();
});
</script>

<style scoped lang="scss">
.status-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  line-height: 1;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  background-color: rgba(3, 155, 229, 0.12);
  color: rgba(3, 155, 229, 1);
}

.config-warning {
  margin-bottom: 1rem;
}

.config-warning-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-warning-link {
  margin-left: 0.25rem;
  font-weight: 600;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;

  .left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .search-field {
    flex: 1;
    max-width: 18rem;
  }
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.required-label::after {
  content: ' *';
  color: $tenant-ui-text-danger;
}
</style>
