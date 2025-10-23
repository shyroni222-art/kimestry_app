{{/*
Expand the name of the chart.
*/}}
{{- define "kimestry-benchmark.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "kimestry-benchmark.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kimestry-benchmark.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kimestry-benchmark.labels" -}}
helm.sh/chart: {{ include "kimestry-benchmark.chart" . }}
{{ include "kimestry-benchmark.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kimestry-benchmark.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kimestry-benchmark.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend-specific helpers
*/}}
{{- define "kimestry-benchmark.backend.name" -}}
{{- default (printf "%s-backend" .Chart.Name) .Values.backend.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "kimestry-benchmark.backend.fullname" -}}
{{- if .Values.backend.fullnameOverride }}
{{- .Values.backend.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default (printf "%s-backend" .Chart.Name) .Values.backend.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "kimestry-benchmark.backend.labels" -}}
helm.sh/chart: {{ include "kimestry-benchmark.chart" . }}
{{ include "kimestry-benchmark.backend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "kimestry-benchmark.backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kimestry-benchmark.backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend-specific helpers
*/}}
{{- define "kimestry-benchmark.frontend.name" -}}
{{- default (printf "%s-frontend" .Chart.Name) .Values.frontend.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "kimestry-benchmark.frontend.fullname" -}}
{{- if .Values.frontend.fullnameOverride }}
{{- .Values.frontend.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default (printf "%s-frontend" .Chart.Name) .Values.frontend.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "kimestry-benchmark.frontend.labels" -}}
helm.sh/chart: {{ include "kimestry-benchmark.chart" . }}
{{ include "kimestry-benchmark.frontend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "kimestry-benchmark.frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kimestry-benchmark.frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}