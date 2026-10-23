
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function getProducts({
  page = 1,
  pageSize = 9,
  search = "",
  minPrice = "",
  maxPrice = "",
  sortBy = "id",
  order = "asc",
} = {}) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    sort_by: sortBy,
    order,
  });

  if (search.trim()) {
    params.set("search", search.trim());
  }

  if (minPrice !== "") {
    params.set("min_price", minPrice);
  }

  if (maxPrice !== "") {
    params.set("max_price", maxPrice);
  }

  const response = await fetch(`${API_URL}/products?${params.toString()}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch products (${response.status})`
    );
  }

  return response.json();
}
