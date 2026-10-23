
import { useEffect, useState } from "react";
import { getProducts } from "./api/products";
import AuthPanel from "./components/AuthPanel";
import "./App.css";

const PAGE_SIZE = 9;

function App() {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const [searchInput, setSearchInput] = useState("");
  const [minPriceInput, setMinPriceInput] = useState("");
  const [maxPriceInput, setMaxPriceInput] = useState("");
  const [retryCount, setRetryCount] = useState(0);

  const [token, setToken] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  const [filters, setFilters] = useState({
    search: "",
    minPrice: "",
    maxPrice: "",
  });

  const [sortBy, setSortBy] = useState("id");
  const [order, setOrder] = useState("asc");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Authentication handlers must be inside App(),
  // but outside useEffect().
  function handleAuthenticated({ token, user }) {
    setToken(token);
    setCurrentUser(user);
  }

  function handleLogout() {
    setToken(null);
    setCurrentUser(null);
  }

  // Load products whenever the listing options change.
  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      setLoading(true);
      setError("");

      try {
        const data = await getProducts({
          page,
          pageSize: PAGE_SIZE,
          search: filters.search,
          minPrice: filters.minPrice,
          maxPrice: filters.maxPrice,
          sortBy,
          order,
        });

        if (cancelled) return;

        setProducts(data.items);
        setTotal(data.total);
        setTotalPages(data.total_pages);
      } catch (err) {
        if (cancelled) return;

        setError(err.message || "Unable to load products.");
        setProducts([]);
        setTotal(0);
        setTotalPages(0);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadProducts();

    return () => {
      cancelled = true;
    };
  }, [page, filters, sortBy, order, retryCount]);

  function handleSearch(event) {
    event.preventDefault();

    if (
      minPriceInput !== "" &&
      maxPriceInput !== "" &&
      Number(minPriceInput) > Number(maxPriceInput)
    ) {
      setError("Minimum price cannot exceed maximum price.");
      return;
    }

    setError("");
    setPage(1);

    setFilters({
      search: searchInput,
      minPrice: minPriceInput,
      maxPrice: maxPriceInput,
    });
  }

  function clearFilters() {
    setSearchInput("");
    setMinPriceInput("");
    setMaxPriceInput("");

    setFilters({
      search: "",
      minPrice: "",
      maxPrice: "",
    });

    setSortBy("id");
    setOrder("asc");
    setPage(1);
    setError("");
  }

  return (
    <main className="container">
      <header className="page-header">
        <p className="eyebrow">YOUR STORE</p>
        <h1>Products</h1>
        <p>Discover and explore our product catalog.</p>
      </header>

      <AuthPanel
        currentUser={currentUser}
        onAuthenticated={handleAuthenticated}
        onLogout={handleLogout}
      />

      <form className="filter-panel" onSubmit={handleSearch}>
        <div className="filter-field search-field">
          <label htmlFor="search">Search products</label>
          <input
            id="search"
            type="search"
            placeholder="Name or description..."
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="min-price">Minimum price (₹)</label>
          <input
            id="min-price"
            type="number"
            min="0"
            step="any"
            placeholder="0"
            value={minPriceInput}
            onChange={(event) => setMinPriceInput(event.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="max-price">Maximum price (₹)</label>
          <input
            id="max-price"
            type="number"
            min="0"
            step="any"
            placeholder="Any"
            value={maxPriceInput}
            onChange={(event) => setMaxPriceInput(event.target.value)}
          />
        </div>

        <div className="filter-actions">
          <button type="submit" className="primary-button">
            Apply filters
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={clearFilters}
          >
            Clear
          </button>
        </div>
      </form>

      <section className="results-toolbar">
        <p>
          {total} matching product{total === 1 ? "" : "s"}
        </p>

        <div className="sort-controls">
          <label htmlFor="sort-by">Sort by</label>

          <select
            id="sort-by"
            value={sortBy}
            onChange={(event) => {
              setSortBy(event.target.value);
              setPage(1);
            }}
          >
            <option value="id">Default</option>
            <option value="name">Name</option>
            <option value="price">Price</option>
          </select>

          <select
            aria-label="Sort order"
            value={order}
            onChange={(event) => {
              setOrder(event.target.value);
              setPage(1);
            }}
          >
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </div>
      </section>

      {loading && <p role="status">Loading products...</p>}

      {!loading && error && (
        <div className="error-panel" role="alert">
          <p>{error}</p>

          <button
            type="button"
            className="secondary-button"
            onClick={() => setRetryCount((current) => current + 1)}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && products.length === 0 && (
        <div className="empty-state">
          <h2>No products found</h2>
          <p>Try changing your search or price filters.</p>
        </div>
      )}

      {!loading && !error && products.length > 0 && (
        <>
          <section className="product-grid" aria-label="Product list">
            {products.map((product) => (
              <article className="product-card" key={product.id}>
                <div className="product-placeholder" aria-hidden="true">
                  {product.name.charAt(0).toUpperCase()}
                </div>

                <div className="product-info">
                  <h2>{product.name}</h2>

                  <p className="price">
                    {new Intl.NumberFormat("en-IN", {
                      style: "currency",
                      currency: "INR",
                      maximumFractionDigits: 2,
                    }).format(product.price)}
                  </p>

                  <p className="description">
                    {product.description || "No description available."}
                  </p>
                </div>
              </article>
            ))}
          </section>

          <nav className="pagination" aria-label="Product pages">
            <button
              type="button"
              className="secondary-button"
              disabled={page <= 1 || loading}
              onClick={() => setPage((current) => current - 1)}
            >
              Previous
            </button>

            <span>
              Page {page} of {totalPages}
            </span>

            <button
              type="button"
              className="secondary-button"
              disabled={page >= totalPages || loading}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </button>
          </nav>
        </>
      )}
    </main>
  );
}

export default App;
