import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Runs `fetcher` on mount and every `intervalMs` after that (default 6s —
 * fast enough to feel "live" on a projector, slow enough not to hammer
 * the API). Pass intervalMs=0 to disable auto-refresh (fetch once only).
 */
export function usePoll(fetcher, { intervalMs = 6000, deps = [] } = {}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const run = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const result = await fetcherRef.current();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    run(false);
    if (!intervalMs) return undefined;
    const id = setInterval(() => run(true), intervalMs);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run, intervalMs, ...deps]);

  return { data, error, loading, refetch: () => run(false) };
}
