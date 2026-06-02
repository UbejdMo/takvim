import { useQuery } from "@tanstack/react-query";

import { api } from "../api/client";

export function useCities() {
  return useQuery({ queryKey: ["cities"], queryFn: api.cities });
}

export function useTodayTimes(city: string) {
  return useQuery({
    queryKey: ["today-times", city],
    queryFn: () => api.todayTimes(city),
    enabled: Boolean(city),
  });
}

export function useTimesOnDate(city: string, date: string) {
  return useQuery({
    queryKey: ["times-on-date", city, date],
    queryFn: () => api.timesOnDate(city, date),
    enabled: Boolean(city && date),
  });
}

export function useMonth(city: string, year: number, month: number) {
  return useQuery({
    queryKey: ["month", city, year, month],
    queryFn: () => api.month(city, year, month),
    enabled: Boolean(city),
  });
}

export function useYear(city: string, year: number) {
  return useQuery({
    queryKey: ["year", city, year],
    queryFn: () => api.year(city, year),
    enabled: Boolean(city),
  });
}

export function useEvents(year: number) {
  return useQuery({ queryKey: ["events", year], queryFn: () => api.events(year) });
}

export function useEventToday() {
  return useQuery({ queryKey: ["event-today"], queryFn: api.eventToday });
}

export function useQibla(city: string) {
  return useQuery({
    queryKey: ["qibla", city],
    queryFn: () => api.qibla(city),
    enabled: Boolean(city),
  });
}
