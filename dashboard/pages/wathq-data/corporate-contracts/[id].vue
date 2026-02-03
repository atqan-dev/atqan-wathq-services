<template>
  <div class="corporate-contract-view">
    <!-- Header with Back Button -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <UButton
          icon="i-heroicons-arrow-left"
          color="gray"
          variant="ghost"
          @click="router.push('/wathq-data/corporate-contracts')"
        >
          {{ t('corporateContracts.view.back') }}
        </UButton>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ contractData?.entity_name || 'Corporate Contract' }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {{ t('corporateContracts.view.fields.contractId') }}: {{ contractData?.contract_id }}
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <UButton
          icon="i-heroicons-printer"
          color="gray"
          variant="outline"
          @click="handlePrint"
        >
          طباعة
        </UButton>
        <UDropdown :items="exportMenuItems" :popper="{ placement: 'bottom-end' }">
          <UButton
            icon="i-heroicons-arrow-down-tray"
            color="primary"
            variant="outline"
            trailing-icon="i-heroicons-chevron-down"
          >
            تصدير
          </UButton>
        </UDropdown>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary-500" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <div class="flex items-center gap-3">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-red-600" />
        <div>
          <h3 class="font-semibold text-red-900 dark:text-red-200">{{ t('corporateContracts.view.errorLoading') }}</h3>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="contractData" class="space-y-6">
      <!-- Overview Cards Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('corporateContracts.view.fields.contractId') }}</p>
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">{{ contractData.contract_id || '-' }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('corporateContracts.view.fields.totalCapital') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{{ formatCurrency(contractData.total_capital) }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('corporateContracts.view.fields.companyDuration') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ contractData.company_duration ? `${contractData.company_duration}` : '-' }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ t('corporateContracts.view.fields.years') }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('corporateContracts.view.sections.parties') }}</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ contractData.parties?.length || 0 }}</p>
          </div>
        </UCard>
      </div>

      <!-- Main Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.mainInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('corporateContracts.view.fields.id')" :value="contractData.id" />
          <InfoField :label="t('corporateContracts.view.fields.contractId')" :value="contractData.contract_id" />
          <InfoField :label="t('corporateContracts.view.fields.contractCopyNumber')" :value="contractData.contract_copy_number" />
          <InfoField :label="t('corporateContracts.view.fields.contractDate')" :value="formatDate(contractData.contract_date)" />
          <InfoField :label="t('corporateContracts.view.fields.crNumber')" :value="contractData.cr_number" />
          <InfoField :label="t('corporateContracts.view.fields.crNationalNumber')" :value="contractData.cr_national_number" />
        </div>
      </UCard>

      <!-- Entity Details Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-building-office" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.entityDetails') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('corporateContracts.view.fields.entityName')" :value="contractData.entity_name" />
          <InfoField :label="t('corporateContracts.view.fields.entityNameLang')" :value="contractData.entity_name_lang_desc" />
          <InfoField :label="t('corporateContracts.view.fields.entityType')" :value="contractData.entity_type_name" />
          <InfoField :label="t('corporateContracts.view.fields.entityForm')" :value="contractData.entity_form_name" />
          <InfoField :label="t('corporateContracts.view.fields.companyDuration')" :value="contractData.company_duration ? `${contractData.company_duration} ${t('corporateContracts.view.fields.years')}` : '-'" />
          <InfoField :label="t('corporateContracts.view.fields.headquarterCity')" :value="contractData.headquarter_city_name" />
          <InfoField :label="t('corporateContracts.view.fields.isLicenseBased')" :value="contractData.is_license_based ? t('corporateContracts.view.fields.yes') : t('corporateContracts.view.fields.no')" />
        </div>
      </UCard>

      <!-- Fiscal Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.fiscalInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('corporateContracts.view.fields.fiscalCalendarType')" :value="contractData.fiscal_calendar_type" />
          <InfoField :label="t('corporateContracts.view.fields.fiscalYearEndMonth')" :value="contractData.fiscal_year_end_month" />
          <InfoField :label="t('corporateContracts.view.fields.fiscalYearEndDay')" :value="contractData.fiscal_year_end_day" />
          <InfoField :label="t('corporateContracts.view.fields.fiscalYearEndYear')" :value="contractData.fiscal_year_end_year" />
        </div>
      </UCard>

      <!-- Capital Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-banknotes" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.capitalInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('corporateContracts.view.fields.currency')" :value="contractData.currency_name" />
          <InfoField :label="t('corporateContracts.view.fields.totalCapital')" :value="formatCurrency(contractData.total_capital)" />
          <InfoField :label="t('corporateContracts.view.fields.paidCapital')" :value="formatCurrency(contractData.paid_capital)" />
          <InfoField :label="t('corporateContracts.view.fields.cashCapital')" :value="formatCurrency(contractData.cash_capital)" />
          <InfoField :label="t('corporateContracts.view.fields.inKindCapital')" :value="formatCurrency(contractData.in_kind_capital)" />
        </div>
      </UCard>

      <!-- Profit Allocation Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-chart-pie" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.profitAllocation') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('corporateContracts.view.fields.isSetAsideEnabled')" :value="contractData.is_set_aside_enabled ? t('corporateContracts.view.fields.yes') : t('corporateContracts.view.fields.no')" />
          <InfoField :label="t('corporateContracts.view.fields.profitAllocationPercentage')" :value="contractData.profit_allocation_percentage ? `${contractData.profit_allocation_percentage}%` : '-'" />
          <InfoField :label="t('corporateContracts.view.fields.profitAllocationPurpose')" :value="contractData.profit_allocation_purpose" />
        </div>
        <div v-if="contractData.additional_decision_text" class="mt-4">
          <InfoField :label="t('corporateContracts.view.fields.additionalDecisionText')" :value="contractData.additional_decision_text" />
        </div>
      </UCard>

      <!-- Audit Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.auditInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('corporateContracts.view.fields.createdAt')" :value="formatDateTime(contractData.created_at)" />
          <InfoField :label="t('corporateContracts.view.fields.updatedAt')" :value="formatDateTime(contractData.updated_at)" />
          <InfoField :label="t('corporateContracts.view.fields.createdBy')" :value="contractData.created_by" />
          <InfoField :label="t('corporateContracts.view.fields.updatedBy')" :value="contractData.updated_by" />
        </div>
      </UCard>

      <!-- Stocks Section -->
      <UCard v-if="contractData.stocks && contractData.stocks.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-chart-bar" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.stocks') }}</h2>
            </div>
            <UBadge color="primary" variant="subtle">{{ contractData.stocks.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.stockType') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.stockCount') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.stockValue') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(stock, index) in contractData.stocks" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ stock.stock_type_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ stock.stock_count || '-' }}</td>
                <td class="px-4 py-3 text-sm font-medium text-green-600 dark:text-green-400">{{ formatCurrency(stock.stock_value) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Parties Section -->
      <UCard v-if="contractData.parties && contractData.parties.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-users" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.parties') }}</h2>
            </div>
            <UBadge color="primary" variant="subtle">{{ contractData.parties.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.partyName') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.partyType') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.identityNumber') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.nationality') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.guardianName') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(party, index) in contractData.parties" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{{ party.name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ party.type_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-mono">{{ party.identity_number || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ party.nationality || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{{ party.guardian_name || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Managers Section -->
      <UCard v-if="contractData.managers && contractData.managers.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-user-circle" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.managers') }}</h2>
            </div>
            <UBadge color="primary" variant="subtle">{{ contractData.managers.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.managerName') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.positionName') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.identityNumber') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.nationality') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.isLicensed') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(manager, index) in contractData.managers" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{{ manager.name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ manager.position_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-mono">{{ manager.identity_number || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ manager.nationality || '-' }}</td>
                <td class="px-4 py-3 text-sm">
                  <UBadge :color="manager.is_licensed ? 'green' : 'gray'" variant="subtle">
                    {{ manager.is_licensed ? t('corporateContracts.view.fields.yes') : t('corporateContracts.view.fields.no') }}
                  </UBadge>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Management Config Section -->
      <UCard v-if="contractData.management_config">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.managementConfig') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('corporateContracts.view.fields.structureName')" :value="contractData.management_config.structure_name" />
          <InfoField :label="t('corporateContracts.view.fields.meetingQuorumName')" :value="contractData.management_config.meeting_quorum_name" />
          <InfoField :label="t('corporateContracts.view.fields.canDelegateAttendance')" :value="contractData.management_config.can_delegate_attendance ? t('corporateContracts.view.fields.yes') : t('corporateContracts.view.fields.no')" />
          <InfoField :label="t('corporateContracts.view.fields.termYears')" :value="contractData.management_config.term_years" />
        </div>
      </UCard>

      <!-- Activities Section -->
      <UCard v-if="contractData.activities && contractData.activities.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-briefcase" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.activities') }}</h2>
            </div>
            <UBadge color="primary" variant="subtle">{{ contractData.activities.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.activityId') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.activityName') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(activity, index) in contractData.activities" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm font-mono text-gray-900 dark:text-white">{{ activity.activity_id || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ activity.activity_name || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Articles Section -->
      <UCard v-if="contractData.articles && contractData.articles.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document-duplicate" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.articles') }} ({{ contractData.articles.length }})</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(article, index) in contractData.articles"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <InfoField :label="t('corporateContracts.view.fields.originalId')" :value="article.original_id" />
              <InfoField :label="t('corporateContracts.view.fields.partName')" :value="article.part_name" />
            </div>
            <div class="mt-4">
              <InfoField :label="t('corporateContracts.view.fields.articleText')" :value="article.article_text" />
            </div>
          </div>
        </div>
      </UCard>

      <!-- Decisions Section -->
      <UCard v-if="contractData.decisions && contractData.decisions.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.decisions') }}</h2>
            </div>
            <UBadge color="primary" variant="subtle">{{ contractData.decisions.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.decisionName') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('corporateContracts.view.fields.approvePercentage') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(decision, index) in contractData.decisions" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ decision.decision_name || '-' }}</td>
                <td class="px-4 py-3 text-sm font-medium text-blue-600 dark:text-blue-400">
                  {{ decision.approve_percentage ? `${decision.approve_percentage}%` : '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Notification Channels Section -->
      <UCard v-if="contractData.notification_channels && contractData.notification_channels.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-bell" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('corporateContracts.view.sections.notificationChannels') }}</h2>
            </div>
            <UBadge color="primary" variant="subtle">{{ contractData.notification_channels.length }}</UBadge>
          </div>
        </template>

        <div class="flex flex-wrap gap-2 p-4">
          <UBadge
            v-for="(channel, index) in contractData.notification_channels"
            :key="index"
            color="blue"
            variant="soft"
            size="lg"
          >
            <UIcon name="i-heroicons-bell" class="w-4 h-4 mr-1" />
            {{ channel.channel_name }}
          </UBadge>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import InfoField from '~/components/ui/InfoField.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const contractData = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const id = computed(() => route.params.id)

// Export menu items
const exportMenuItems = [
  [
    {
      label: 'تصدير JSON',
      icon: 'i-heroicons-code-bracket',
      click: () => handleExportJSON()
    },
    {
      label: 'تصدير CSV',
      icon: 'i-heroicons-document',
      click: () => handleExportCSV()
    },
    {
      label: 'تصدير XLS',
      icon: 'i-heroicons-table-cells',
      click: () => handleExportXLS()
    },
    {
      label: 'تصدير PDF',
      icon: 'i-heroicons-document-text',
      click: () => handleExportPDF()
    },
    {
      label: 'Preview Template',
      icon: 'i-heroicons-eye',
      click: () => handlePreviewTemplate()
    }
  ]
]

// Mock data for development
const getMockContractData = (id: number) => {
  return {
    id: id,
    contract_id: 12345,
    contract_copy_number: 1,
    contract_date: '2024-01-15',
    cr_national_number: '7001234567',
    cr_number: '1010711252',
    entity_name: 'شركة التقنية السعودية',
    entity_name_lang_desc: 'Saudi Technology Company',
    company_duration: 99,
    headquarter_city_name: 'الرياض',
    is_license_based: false,
    entity_type_name: 'شركة',
    entity_form_name: 'ذات مسؤولية محدودة',
    fiscal_calendar_type: 'ميلادي',
    fiscal_year_end_month: 12,
    fiscal_year_end_day: 31,
    fiscal_year_end_year: 2024,
    currency_name: 'ريال سعودي',
    total_capital: 5000000,
    paid_capital: 5000000,
    cash_capital: 2500000,
    in_kind_capital: 2500000,
    is_set_aside_enabled: true,
    profit_allocation_percentage: 10,
    profit_allocation_purpose: 'احتياطي قانوني',
    additional_decision_text: 'قرار إضافي بشأن توزيع الأرباح',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    created_by: 1,
    updated_by: 1,
    request_body: null,
    stocks: [
      {
        id: 1,
        contract_id: id,
        stock_type_name: 'أسهم عادية',
        stock_count: 1000,
        stock_value: 5000
      }
    ],
    parties: [
      {
        id: 1,
        contract_id: id,
        name: 'أحمد محمد السعيد',
        type_name: 'شريك',
        identity_number: '1234567890',
        identity_type: 'هوية وطنية',
        nationality: 'سعودي',
        guardian_name: null,
        guardian_identity_number: null,
        is_father_guardian: null
      }
    ],
    managers: [
      {
        id: 1,
        contract_id: id,
        name: 'محمد أحمد الرشيد',
        type_name: 'مدير تنفيذي',
        is_licensed: true,
        identity_number: '9876543210',
        nationality: 'سعودي',
        position_name: 'الرئيس التنفيذي'
      }
    ],
    management_config: {
      id: 1,
      contract_id: id,
      structure_name: 'مجلس إدارة',
      meeting_quorum_name: 'الأغلبية البسيطة',
      can_delegate_attendance: true,
      term_years: 3
    },
    activities: [
      {
        id: 1,
        contract_id: id,
        activity_id: '6201',
        activity_name: 'تطوير البرمجيات'
      },
      {
        id: 2,
        contract_id: id,
        activity_id: '6202',
        activity_name: 'الاستشارات التقنية'
      }
    ],
    articles: [
      {
        id: 1,
        contract_id: id,
        original_id: 1,
        article_text: 'المادة الأولى: تأسيس الشركة',
        part_name: 'الباب الأول'
      }
    ],
    decisions: [
      {
        id: 1,
        contract_id: id,
        decision_name: 'قرار توزيع الأرباح',
        approve_percentage: 75
      }
    ],
    notification_channels: [
      {
        id: 1,
        contract_id: id,
        channel_name: 'البريد الإلكتروني'
      },
      {
        id: 2,
        contract_id: id,
        channel_name: 'الرسائل النصية'
      }
    ]
  }
}

onMounted(async () => {
  await fetchContractData()
})

async function fetchContractData() {
  loading.value = true
  error.value = null
  
  try {
    console.log('Fetching contract data for ID:', id.value)
    const response = await $fetch(`/api/v1/wathq/corporate-contracts/${id.value}`)
    console.log('API Response:', response)
    
    // API returns the contract object directly with all relations
    if (response) {
      contractData.value = response
      console.log('Contract Data loaded from API:', contractData.value)
    } else {
      throw new Error('No data returned from API')
    }
  } catch (err: any) {
    console.warn('API call failed, using mock data:', err)
    error.value = err.message || 'Failed to load contract data'
    // Fallback to mock data for development
    contractData.value = getMockContractData(Number(id.value))
    console.log('Using mock contract data:', contractData.value)
  } finally {
    loading.value = false
  }
}

function handlePrint() {
  window.print()
}

function handleExportJSON() {
  if (!contractData.value) return
  
  const dataStr = JSON.stringify(contractData.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `corporate_contract_${id.value}.json`
  link.click()
  URL.revokeObjectURL(url)
}

function handleExportCSV() {
  if (!contractData.value) return
  
  // Convert contract data to CSV format with UTF-8 BOM for proper Arabic support
  const BOM = '\uFEFF'
  const headers = ['Field', 'Value']
  
  const rows = [
    ['Contract ID', contractData.value.contract_id],
    ['Contract Copy Number', contractData.value.contract_copy_number],
    ['Contract Date', contractData.value.contract_date],
    ['CR Number', contractData.value.cr_number],
    ['CR National Number', contractData.value.cr_national_number],
    ['Entity Name', contractData.value.entity_name],
    ['Entity Name (Lang)', contractData.value.entity_name_lang_desc],
    ['Entity Type', contractData.value.entity_type_name],
    ['Entity Form', contractData.value.entity_form_name],
    ['Company Duration', contractData.value.company_duration],
    ['Headquarter City', contractData.value.headquarter_city_name],
    ['Is License Based', contractData.value.is_license_based ? 'Yes' : 'No'],
    ['Currency', contractData.value.currency_name],
    ['Total Capital', contractData.value.total_capital],
    ['Paid Capital', contractData.value.paid_capital],
    ['Cash Capital', contractData.value.cash_capital],
    ['In-Kind Capital', contractData.value.in_kind_capital],
    ['Fiscal Calendar Type', contractData.value.fiscal_calendar_type],
    ['Profit Allocation %', contractData.value.profit_allocation_percentage],
  ]
  
  let csvContent = BOM + headers.join(',') + '\n'
  rows.forEach(row => {
    csvContent += row.map(cell => `"${cell || ''}"`).join(',') + '\n'
  })
  
  // Add parties section
  if (contractData.value.parties && contractData.value.parties.length > 0) {
    csvContent += '\n\nParties\n'
    csvContent += 'Name,Type,Identity Number,Identity Type,Nationality,Guardian Name\n'
    contractData.value.parties.forEach((party: any) => {
      csvContent += `"${party.name || ''}","${party.type_name || ''}","${party.identity_number || ''}","${party.identity_type || ''}","${party.nationality || ''}","${party.guardian_name || ''}"\n`
    })
  }
  
  // Add managers section
  if (contractData.value.managers && contractData.value.managers.length > 0) {
    csvContent += '\n\nManagers\n'
    csvContent += 'Name,Position,Identity Number,Nationality,Licensed\n'
    contractData.value.managers.forEach((manager: any) => {
      csvContent += `"${manager.name || ''}","${manager.position_name || ''}","${manager.identity_number || ''}","${manager.nationality || ''}","${manager.is_licensed ? 'Yes' : 'No'}"\n`
    })
  }
  
  // Add stocks section
  if (contractData.value.stocks && contractData.value.stocks.length > 0) {
    csvContent += '\n\nStocks\n'
    csvContent += 'Stock Type,Count,Value\n'
    contractData.value.stocks.forEach((stock: any) => {
      csvContent += `"${stock.stock_type_name || ''}","${stock.stock_count || ''}","${stock.stock_value || ''}"\n`
    })
  }
  
  // Add activities section
  if (contractData.value.activities && contractData.value.activities.length > 0) {
    csvContent += '\n\nActivities\n'
    csvContent += 'Activity ID,Activity Name\n'
    contractData.value.activities.forEach((activity: any) => {
      csvContent += `"${activity.activity_id || ''}","${activity.activity_name || ''}"\n`
    })
  }
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `corporate_contract_${id.value}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

function handleExportXLS() {
  if (!contractData.value) return
  
  // Create HTML table for Excel export
  let htmlContent = `
    <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
    <head>
      <meta charset="utf-8">
      <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
        th { background-color: #4CAF50; color: white; font-weight: bold; }
        .section-header { background-color: #2196F3; color: white; font-weight: bold; font-size: 14px; }
      </style>
    </head>
    <body>
      <table>
        <tr><th colspan="2" class="section-header">معلومات العقد الأساسية / Contract Main Information</th></tr>
        <tr><td><b>Contract ID</b></td><td>${contractData.value.contract_id || ''}</td></tr>
        <tr><td><b>Contract Copy Number</b></td><td>${contractData.value.contract_copy_number || ''}</td></tr>
        <tr><td><b>Contract Date</b></td><td>${contractData.value.contract_date || ''}</td></tr>
        <tr><td><b>CR Number</b></td><td>${contractData.value.cr_number || ''}</td></tr>
        <tr><td><b>CR National Number</b></td><td>${contractData.value.cr_national_number || ''}</td></tr>
        <tr><td><b>Entity Name</b></td><td>${contractData.value.entity_name || ''}</td></tr>
        <tr><td><b>Entity Name (Lang)</b></td><td>${contractData.value.entity_name_lang_desc || ''}</td></tr>
        <tr><td><b>Entity Type</b></td><td>${contractData.value.entity_type_name || ''}</td></tr>
        <tr><td><b>Entity Form</b></td><td>${contractData.value.entity_form_name || ''}</td></tr>
        <tr><td><b>Company Duration</b></td><td>${contractData.value.company_duration || ''}</td></tr>
        <tr><td><b>Headquarter City</b></td><td>${contractData.value.headquarter_city_name || ''}</td></tr>
        <tr><td><b>Is License Based</b></td><td>${contractData.value.is_license_based ? 'Yes' : 'No'}</td></tr>
        
        <tr><th colspan="2" class="section-header">معلومات رأس المال / Capital Information</th></tr>
        <tr><td><b>Currency</b></td><td>${contractData.value.currency_name || ''}</td></tr>
        <tr><td><b>Total Capital</b></td><td>${contractData.value.total_capital || ''}</td></tr>
        <tr><td><b>Paid Capital</b></td><td>${contractData.value.paid_capital || ''}</td></tr>
        <tr><td><b>Cash Capital</b></td><td>${contractData.value.cash_capital || ''}</td></tr>
        <tr><td><b>In-Kind Capital</b></td><td>${contractData.value.in_kind_capital || ''}</td></tr>
        
        <tr><th colspan="2" class="section-header">السنة المالية / Fiscal Year</th></tr>
        <tr><td><b>Fiscal Calendar Type</b></td><td>${contractData.value.fiscal_calendar_type || ''}</td></tr>
        <tr><td><b>Fiscal Year End</b></td><td>${contractData.value.fiscal_year_end_day || ''}/${contractData.value.fiscal_year_end_month || ''}/${contractData.value.fiscal_year_end_year || ''}</td></tr>
        
        <tr><th colspan="2" class="section-header">توزيع الأرباح / Profit Allocation</th></tr>
        <tr><td><b>Set Aside Enabled</b></td><td>${contractData.value.is_set_aside_enabled ? 'Yes' : 'No'}</td></tr>
        <tr><td><b>Profit Allocation %</b></td><td>${contractData.value.profit_allocation_percentage || ''}%</td></tr>
        <tr><td><b>Profit Allocation Purpose</b></td><td>${contractData.value.profit_allocation_purpose || ''}</td></tr>
      </table>
  `
  
  // Add Parties table
  if (contractData.value.parties && contractData.value.parties.length > 0) {
    htmlContent += `
      <br/><br/>
      <table>
        <tr><th colspan="6" class="section-header">الشركاء / Parties</th></tr>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Identity Number</th>
          <th>Identity Type</th>
          <th>Nationality</th>
          <th>Guardian Name</th>
        </tr>
    `
    contractData.value.parties.forEach((party: any) => {
      htmlContent += `
        <tr>
          <td>${party.name || ''}</td>
          <td>${party.type_name || ''}</td>
          <td>${party.identity_number || ''}</td>
          <td>${party.identity_type || ''}</td>
          <td>${party.nationality || ''}</td>
          <td>${party.guardian_name || ''}</td>
        </tr>
      `
    })
    htmlContent += '</table>'
  }
  
  // Add Managers table
  if (contractData.value.managers && contractData.value.managers.length > 0) {
    htmlContent += `
      <br/><br/>
      <table>
        <tr><th colspan="5" class="section-header">المديرون / Managers</th></tr>
        <tr>
          <th>Name</th>
          <th>Position</th>
          <th>Identity Number</th>
          <th>Nationality</th>
          <th>Licensed</th>
        </tr>
    `
    contractData.value.managers.forEach((manager: any) => {
      htmlContent += `
        <tr>
          <td>${manager.name || ''}</td>
          <td>${manager.position_name || ''}</td>
          <td>${manager.identity_number || ''}</td>
          <td>${manager.nationality || ''}</td>
          <td>${manager.is_licensed ? 'Yes' : 'No'}</td>
        </tr>
      `
    })
    htmlContent += '</table>'
  }
  
  // Add Stocks table
  if (contractData.value.stocks && contractData.value.stocks.length > 0) {
    htmlContent += `
      <br/><br/>
      <table>
        <tr><th colspan="3" class="section-header">الأسهم / Stocks</th></tr>
        <tr>
          <th>Stock Type</th>
          <th>Count</th>
          <th>Value</th>
        </tr>
    `
    contractData.value.stocks.forEach((stock: any) => {
      htmlContent += `
        <tr>
          <td>${stock.stock_type_name || ''}</td>
          <td>${stock.stock_count || ''}</td>
          <td>${stock.stock_value || ''}</td>
        </tr>
      `
    })
    htmlContent += '</table>'
  }
  
  // Add Activities table
  if (contractData.value.activities && contractData.value.activities.length > 0) {
    htmlContent += `
      <br/><br/>
      <table>
        <tr><th colspan="2" class="section-header">الأنشطة / Activities</th></tr>
        <tr>
          <th>Activity ID</th>
          <th>Activity Name</th>
        </tr>
    `
    contractData.value.activities.forEach((activity: any) => {
      htmlContent += `
        <tr>
          <td>${activity.activity_id || ''}</td>
          <td>${activity.activity_name || ''}</td>
        </tr>
      `
    })
    htmlContent += '</table>'
  }
  
  htmlContent += '</body></html>'
  
  // Create blob and download
  const blob = new Blob([htmlContent], { type: 'application/vnd.ms-excel;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `corporate_contract_${id.value}.xls`
  link.click()
  URL.revokeObjectURL(url)
}

async function handleExportPDF() {
  if (!id.value) return
  
  try {
    // Call the backend PDF export endpoint with authentication
    const response = await $fetch(`/api/v1/wathq/pdf/database/corporate-contract/${id.value}/pdf`, {
      method: 'GET',
      responseType: 'blob'
    })
    
    // Create blob URL and download
    const blob = new Blob([response], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `corporate_contract_${id.value}.pdf`
    link.click()
    URL.revokeObjectURL(url)
  } catch (err: any) {
    console.error('Failed to export PDF:', err)
    alert('فشل في تصدير PDF. يرجى المحاولة مرة أخرى.')
  }
}

async function handlePreviewTemplate() {
  if (!id.value) return
  
  try {
    // Fetch the HTML preview with authentication
    const htmlContent = await $fetch(`/api/v1/wathq/pdf/database/corporate-contract/${id.value}/preview`, {
      method: 'GET'
    })
    
    // Open in new window with the HTML content
    const newWindow = window.open('', '_blank')
    if (newWindow) {
      newWindow.document.write(htmlContent as string)
      newWindow.document.close()
    }
  } catch (err: any) {
    console.error('Failed to preview template:', err)
    alert('فشل في معاينة القالب. يرجى المحاولة مرة أخرى.')
  }
}

function formatDate(dateString: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('ar-SA')
}

function formatDateTime(dateString: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('ar-SA')
}

function formatCurrency(value: any) {
  if (!value) return '-'
  return new Intl.NumberFormat('ar-SA', {
    style: 'currency',
    currency: 'SAR'
  }).format(value)
}
</script>

<style scoped>
.corporate-contract-view {
  @apply space-y-6;
}
</style>
