"""REST API routes for OneTrueAddress system."""
from flask import Blueprint, request, jsonify
from address_agent import AddressAgent
import traceback

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

# Global agent instance
_agent = None

def get_agent():
    """Get or create the address agent instance."""
    global _agent
    if _agent is None:
        _agent = AddressAgent()
    return _agent


@api.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON: {"status": "ok", "version": "1.0"}
    """
    return jsonify({
        'status': 'ok',
        'version': '1.0',
        'service': 'OneTrueAddress API'
    })


@api.route('/match', methods=['POST'])
def match_address():
    """
    Match an address against Golden Source and Internal databases.
    
    Request Body:
        {
            "address": "123 Main St, City, State 12345",
            "threshold": 90  // Optional, defaults to 90
        }
    
    Response:
        {
            "success": true,
            "match_found": true,
            "confidence": 95.5,
            "input_address": "123 Main St...",
            "matched_address": {...},
            "golden_source_matches": [...],
            "internal_matches": [...],
            "total_golden_source": 2,
            "total_internal": 3,
            "has_golden_source": true,
            "has_internal": true,
            "reasoning": "...",
            "business_rule_exception": false,
            "confidence_threshold": 90.0,
            "candidates_searched": 5,
            "search_method": "fuzzy_match_with_ai"
        }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        input_address = data.get('address', '').strip()
        threshold = data.get('threshold', None)
        
        if not input_address:
            return jsonify({
                'success': False,
                'error': 'Address is required'
            }), 400
        
        # Validate threshold if provided
        if threshold is not None:
            try:
                threshold = float(threshold)
                if threshold < 75 or threshold > 100:
                    return jsonify({
                        'success': False,
                        'error': 'Threshold must be between 75 and 100'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Threshold must be a number'
                }), 400
        
        # Perform address matching
        agent = get_agent()
        result = agent.match_address(input_address, threshold=threshold)
        
        # Format response
        response_data = {
            'success': True,
            'input_address': result.get('input_address', input_address),
            'candidates_searched': result.get('candidates_searched', 0),
            'confidence_threshold': result.get('confidence_threshold', 90.0),
            'search_method': result.get('search_method', 'unknown')
        }
        
        # Handle fuzzy match response format
        if result.get('search_method') in ['fuzzy_match', 'fuzzy_match_with_ai']:
            response_data['match_found'] = result.get('match_found', False)
            response_data['confidence'] = result.get('confidence', 0)
            response_data['similarity_score'] = result.get('similarity_score', 0)
            response_data['reasoning'] = result.get('reasoning', 'N/A')
            response_data['business_rule_exception'] = result.get('business_rule_exception', False)
            
            if response_data['match_found']:
                best_match = result.get('best_match', {})
                response_data['matched_address'] = best_match
                response_data['source_table'] = best_match.get('_source_table', 'Unknown')
                response_data['source_type'] = best_match.get('_source_type', 'unknown')
                
                # Include match lists
                golden_source_matches = result.get('golden_source_matches', [])
                internal_matches = result.get('internal_matches', [])
                
                response_data['golden_source_matches'] = golden_source_matches
                response_data['internal_matches'] = internal_matches
                response_data['total_golden_source'] = len(golden_source_matches)
                response_data['total_internal'] = len(internal_matches)
                response_data['has_golden_source'] = result.get('has_golden_source', False)
                response_data['has_internal'] = result.get('has_internal', False)
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@api.route('/consolidate', methods=['POST'])
def consolidate_records():
    """
    Consolidate multiple internal records with Golden Source address.
    
    Request Body:
        {
            "internal_matches": [...],
            "golden_source_address": {...},
            "scenario": 1  // 1=Multiple Matches, 2=Single Mismatch, 3=No Internal
        }
    
    Response:
        {
            "success": true,
            "consolidated_record": {...},
            "message": "Consolidated 3 records successfully"
        }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        internal_matches = data.get('internal_matches', [])
        golden_source_address = data.get('golden_source_address', {})
        scenario = data.get('scenario', 1)
        
        if not internal_matches:
            return jsonify({
                'success': False,
                'error': 'internal_matches is required'
            }), 400
        
        if not golden_source_address:
            return jsonify({
                'success': False,
                'error': 'golden_source_address is required'
            }), 400
        
        # Consolidate records
        agent = get_agent()
        consolidation_result = agent.golden_source.consolidate_internal_records(
            internal_matches, 
            golden_source_address, 
            scenario
        )
        
        if consolidation_result['status'] == 'error':
            return jsonify({
                'success': False,
                'error': consolidation_result['error'],
                'requires_manual_review': consolidation_result.get('requires_manual_review', False)
            }), 400
        
        return jsonify({
            'success': True,
            'consolidated_record': consolidation_result['consolidated_record'],
            'message': consolidation_result.get('message', 'Records consolidated successfully')
        })
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@api.route('/push_updates', methods=['POST'])
def push_updates():
    """
    Push consolidated record to internal_updates table.
    
    Request Body:
        {
            "internal_matches": [...],
            "golden_source_address": {...},
            "scenario": 1  // 1=Multiple Matches, 2=Single Mismatch, 3=No Internal
        }
    
    Response:
        {
            "success": true,
            "message": "Record successfully pushed...",
            "consolidated_record": {...}
        }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        internal_matches = data.get('internal_matches', [])
        golden_source_address = data.get('golden_source_address', {})
        scenario = data.get('scenario', 1)
        
        if not internal_matches:
            return jsonify({
                'success': False,
                'error': 'internal_matches is required'
            }), 400
        
        if not golden_source_address:
            return jsonify({
                'success': False,
                'error': 'golden_source_address is required'
            }), 400
        
        # Get agent and consolidate records
        agent = get_agent()
        
        # Step 1: Consolidate the records
        consolidation_result = agent.golden_source.consolidate_internal_records(
            internal_matches, 
            golden_source_address, 
            scenario
        )
        
        if consolidation_result['status'] == 'error':
            return jsonify({
                'success': False,
                'error': consolidation_result['error'],
                'requires_manual_review': consolidation_result.get('requires_manual_review', False)
            }), 400
        
        # Step 2: Push to internal_updates table
        consolidated_record = consolidation_result['consolidated_record']
        push_result = agent.golden_source.push_to_internal_updates(consolidated_record, scenario)
        
        if push_result['status'] == 'error':
            return jsonify({
                'success': False,
                'error': push_result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'message': push_result['message'],
            'consolidated_record': consolidated_record
        })
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@api.route('/write_to_internal', methods=['POST'])
def write_to_internal():
    """
    Write Golden Source record to internal_updates table.
    
    Request Body:
        {
            "golden_source_record": {...}
        }
    
    Response:
        {
            "success": true,
            "message": "Record successfully pushed...",
            "written_record": {...}
        }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        golden_source_record = data.get('golden_source_record', {})
        
        if not golden_source_record:
            return jsonify({
                'success': False,
                'error': 'golden_source_record is required'
            }), 400
        
        # Get agent and transform record
        agent = get_agent()
        
        # Transform Golden Source to Internal format
        internal_record = agent.golden_source._map_golden_source_to_internal(golden_source_record)
        
        if not internal_record:
            return jsonify({
                'success': False,
                'error': 'Failed to transform Golden Source record to Internal format'
            }), 400
        
        # Push to internal_updates table (Scenario 3: No Internal Match)
        push_result = agent.golden_source.push_to_internal_updates(internal_record, scenario=3)
        
        if push_result['status'] == 'error':
            return jsonify({
                'success': False,
                'error': push_result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'message': push_result['message'],
            'written_record': internal_record
        })
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@api.route('/time_saved', methods=['GET'])
def time_saved():
    """
    Get total time saved by the system.
    
    Response:
        {
            "success": true,
            "hours_saved": 12.5
        }
    """
    try:
        agent = get_agent()
        result = agent.golden_source.get_time_saved()
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'hours_saved': result['hours_saved']
            })
        else:
            return jsonify({
                'success': False,
                'hours_saved': 0.0,
                'error': result.get('error', 'Unknown error')
            })
            
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'hours_saved': 0.0,
            'error': error_msg
        }), 500

