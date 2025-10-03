"use client";

import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';

export function useFilterParams<T extends Record<string, string>>(defaultFilters: T) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const storageKey = `filters_${pathname}`;
  
  const loadFromStorage = useCallback((): T => {
    if (typeof window === 'undefined') return defaultFilters;
    try {
      const saved = sessionStorage.getItem(storageKey);
      return saved ? { ...defaultFilters, ...JSON.parse(saved) } : defaultFilters;
    } catch {
      return defaultFilters;
    }
  }, [defaultFilters, storageKey]);
  
  const saveToStorage = useCallback((filtersToSave: T) => {
    if (typeof window === 'undefined') return;
    try {
      const toStore: Partial<T> = {};
      for (const key in filtersToSave) {
        if (filtersToSave[key] !== defaultFilters[key] && 
            filtersToSave[key] !== '' && 
            filtersToSave[key] !== 'tous') {
          toStore[key] = filtersToSave[key];
        }
      }
      if (Object.keys(toStore).length > 0) {
        sessionStorage.setItem(storageKey, JSON.stringify(toStore));
      } else {
        sessionStorage.removeItem(storageKey);
      }
    } catch {}
  }, [defaultFilters, storageKey]);
  
  const [filters, setFilters] = useState<T>(() => {
    const loaded = { ...defaultFilters };
    let hasUrlParams = false;
    
    for (const key in defaultFilters) {
      const value = searchParams.get(key);
      if (value !== null) {
        loaded[key as keyof T] = value as T[keyof T];
        hasUrlParams = true;
      }
    }
    
    return hasUrlParams ? loaded : loadFromStorage();
  });
  
  useEffect(() => {
    const loaded = { ...defaultFilters };
    let hasUrlParams = false;
    
    for (const key in defaultFilters) {
      const value = searchParams.get(key);
      if (value !== null) {
        loaded[key as keyof T] = value as T[keyof T];
        hasUrlParams = true;
      }
    }
    
    if (hasUrlParams) {
      setFilters(loaded);
      saveToStorage(loaded);
    } else {
      setFilters(loadFromStorage());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  const updateURL = useCallback((newFilters: T) => {
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== defaultFilters[key as keyof T] && value !== '' && value !== 'tous') {
        params.set(key, String(value));
      }
    });
    const newURL = params.toString() ? `${pathname}?${params.toString()}` : pathname;
    router.replace(newURL, { scroll: false });
  }, [pathname, router, defaultFilters]);
  
  const updateFilter = useCallback(<K extends keyof T>(key: K, value: T[K]) => {
    setFilters((prev) => {
      const newFilters = { ...prev, [key]: value };
      updateURL(newFilters);
      saveToStorage(newFilters);
      return newFilters;
    });
  }, [updateURL, saveToStorage]);
  
  const updateFilters = useCallback((updates: Partial<T>) => {
    setFilters((prev) => {
      const newFilters = { ...prev, ...updates };
      updateURL(newFilters);
      saveToStorage(newFilters);
      return newFilters;
    });
  }, [updateURL, saveToStorage]);
  
  const resetFilters = useCallback(() => {
    setFilters(defaultFilters);
    router.replace(pathname, { scroll: false });
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(storageKey);
    }
  }, [defaultFilters, pathname, router, storageKey]);
  
  return { filters, updateFilter, updateFilters, resetFilters };
}
