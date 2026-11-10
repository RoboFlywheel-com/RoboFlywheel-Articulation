// SPDX-License-Identifier: Apache-2.0

import { QueryClient } from "@tanstack/react-query";

export const viewerQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5_000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
