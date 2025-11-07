# Bulk Insert Design - Best Practices for SQL Server

## Question
What is the best practice to import or insert bulk data into SQL Server? Are we inserting row by row?

## Answer
**No, we should NOT insert row by row.** The original implementation used MERGE statements executed once per row, which is inefficient for large datasets. Here are the best practices:

## SQL Server Bulk Insert Methods

### 1. **SqlBulkCopy (Recommended for .NET/PowerShell)** ✅
**What it is:**
- .NET class that provides high-performance bulk loading
- Uses the same bulk insert mechanism as BCP and BULK INSERT
- Minimal logging and optimized for speed

**Performance:**
- **10-100x faster** than row-by-row inserts
- Can insert 10,000+ rows per second
- Uses minimal transaction log space

**Implementation:**
```powershell
$bulkCopy = New-Object System.Data.SqlClient.SqlBulkCopy($connection)
$bulkCopy.DestinationTableName = "ADUsers"
$bulkCopy.BatchSize = 5000
$bulkCopy.WriteToServer($dataTable)
```

**Best for:**
- Large datasets (1000+ rows)
- Initial loads
- Full syncs

### 2. **Table-Valued Parameters (TVPs)**
**What it is:**
- Pass a DataTable as a parameter to a stored procedure
- SQL Server treats it as a table

**Performance:**
- Fast for medium datasets (100-10,000 rows)
- Good for upserts with MERGE

**Best for:**
- Upsert operations (INSERT/UPDATE)
- Medium-sized batches
- When you need transaction control

### 3. **BULK INSERT / BCP**
**What it is:**
- Native SQL Server bulk loading from files
- Fastest for very large datasets

**Performance:**
- Fastest method (can do millions of rows)
- Requires file I/O

**Best for:**
- Very large datasets (100,000+ rows)
- File-based imports
- ETL processes

### 4. **MERGE with Staging Table (Hybrid Approach)** ✅
**What it is:**
- Bulk insert to staging table using SqlBulkCopy
- Then MERGE from staging to target table
- Best of both worlds

**Performance:**
- Fast bulk insert + efficient upsert
- Single transaction
- Handles both inserts and updates

**Best for:**
- Upsert operations (our use case)
- Large datasets with updates
- When you need to track inserts vs updates

## Performance Comparison

| Method | 1,000 Rows | 10,000 Rows | 100,000 Rows | Notes |
|--------|-----------|-------------|--------------|-------|
| Row-by-row INSERT | ~10 sec | ~100 sec | ~1000 sec | ❌ Slow |
| Row-by-row MERGE | ~15 sec | ~150 sec | ~1500 sec | ❌ Slow |
| SqlBulkCopy | ~0.5 sec | ~2 sec | ~15 sec | ✅ Fast |
| TVP + MERGE | ~1 sec | ~5 sec | ~30 sec | ✅ Good |
| Staging + MERGE | ~0.8 sec | ~3 sec | ~20 sec | ✅ Best for upserts |

## Our Implementation Strategy

### Original (Inefficient):
```powershell
foreach ($user in $users) {
    # Execute MERGE once per user
    $mergeCommand.ExecuteNonQuery()
}
# Result: 1000 users = 1000 database round trips
```

### Optimized (Bulk):
```powershell
# 1. Bulk insert all users to staging table (1 operation)
$bulkCopy.WriteToServer($dataTable)

# 2. MERGE from staging to target (1 operation)
MERGE target FROM staging ...
# Result: 1000 users = 2 database operations
```

## Implementation Details

### Staging Table Approach
1. **Create temporary staging table** (in-memory or tempdb)
2. **Bulk insert** all data to staging using SqlBulkCopy
3. **MERGE** from staging to target table
4. **Drop staging table**

**Benefits:**
- ✅ Single bulk insert operation
- ✅ Single MERGE operation
- ✅ Minimal database round trips
- ✅ Transaction-safe
- ✅ Can track inserts vs updates

### Batch Size Considerations
- **Small batches (100-1000)**: Lower memory, more operations
- **Medium batches (1000-5000)**: Good balance (recommended)
- **Large batches (5000-10000)**: Higher memory, fewer operations
- **Very large batches (10000+)**: May cause timeouts

**Recommendation:** Start with 5000, adjust based on:
- Available memory
- Network latency
- Database performance

## Code Example

```powershell
# Create DataTable
$dataTable = New-Object System.Data.DataTable
# ... add columns ...

# Populate DataTable
foreach ($user in $users) {
    $row = $dataTable.NewRow()
    # ... set values ...
    $dataTable.Rows.Add($row)
}

# Bulk insert to staging
$bulkCopy = New-Object System.Data.SqlClient.SqlBulkCopy($connection)
$bulkCopy.DestinationTableName = "#StagingTable"
$bulkCopy.BatchSize = 5000
$bulkCopy.WriteToServer($dataTable)

# MERGE from staging to target
$mergeQuery = "MERGE target FROM staging ..."
$mergeCmd.ExecuteNonQuery()
```

## When to Use Each Method

| Scenario | Recommended Method |
|----------|-------------------|
| Initial load, inserts only | SqlBulkCopy directly to target |
| Upsert (insert + update) | Staging table + MERGE |
| Small batches (< 100 rows) | Row-by-row is acceptable |
| Very large datasets (> 1M rows) | BCP or multiple batches |
| Need transaction control | Staging table + MERGE |

## Conclusion

**For AD object synchronization:**
1. ✅ Use **Staging Table + MERGE** approach
2. ✅ Use **SqlBulkCopy** for bulk insert to staging
3. ✅ Use **batch size of 5000** as default
4. ✅ This provides **10-100x performance improvement** over row-by-row

The new `Write-ADUsersBulk` function implements this best practice.
